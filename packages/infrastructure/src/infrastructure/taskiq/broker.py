from taskiq_redis import ListQueueBroker

from application.settings import Settings

_settings = Settings()

broker = ListQueueBroker(url=_settings.redis.url)
