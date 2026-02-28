
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import coaches, members, plans
from bootstrap.context import ApiApplicationContext


def create_api(ctx: ApiApplicationContext | None = None) -> FastAPI:
    ctx = ctx or ApiApplicationContext()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await ctx.start()
        yield
        await ctx.stop()

    ctx.container.wire(packages=["api.routers"])

    app = FastAPI(title="Personal Training Studio API", lifespan=lifespan)
    app.container = ctx.container  # type: ignore[attr-defined]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(members.router)
    app.include_router(coaches.router)
    app.include_router(plans.router)
    return app


api = create_api()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:api", host="0.0.0.0", port=8000, reload=True)
