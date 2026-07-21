from celery import Celery

from ecommerce_agent.config import Settings

settings = Settings()
celery_app = Celery("ecommerce_agent", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"], timezone="Asia/Shanghai", enable_utc=True)


@celery_app.task(name="knowledge.normalize_markdown")  # type: ignore[untyped-decorator]
def normalize_markdown_task(text: str) -> str:
    from ecommerce_agent.rag.normalizer import normalize_markdown

    return normalize_markdown(text)
