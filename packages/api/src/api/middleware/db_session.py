"""
Pure ASGI middleware for per-request database session management.

Why not Starlette's BaseHTTPMiddleware?
---------------------------------------
BaseHTTPMiddleware.dispatch() calls `call_next(request)` which internally spawns a
**new anyio task** (via `task_group.start_soon`) to run the downstream ASGI app.
Python's ContextVar is copied into that child task at spawn time, but the copy is
a snapshot — any ContextVar.set() done inside the child task is invisible to the
parent, and vice versa.

This means a ContextVar holding the current DB session, set in dispatch() before
call_next(), may not propagate correctly to the handler, or worse — under high
concurrency (e.g. 600 VU load test) a session from one request can leak into
another request's child task if task scheduling interleaves token set/reset
across parent tasks.

Solution: a pure ASGI middleware that wraps `self.app(scope, receive, send)`
directly. This keeps the entire request lifecycle — middleware + handler — in
the **same async task**, so ContextVar set/reset is correctly scoped per request
with no cross-task leakage.
"""

import logging
import os

from starlette.types import ASGIApp, Receive, Scope, Send

_logger = logging.getLogger(__name__)


class DbSessionMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        pid = os.getpid()
        _logger.debug("[pid=%s] Opening transaction for %s %s", pid, scope["method"], scope["path"])
        tm = scope["app"].container.transaction_manager()
        async with tm.transaction():
            await self.app(scope, receive, send)
        _logger.debug("[pid=%s] Closed transaction for %s %s", pid, scope["method"], scope["path"])
