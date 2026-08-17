from uuid import UUID

from celery.utils.log import get_task_logger

from app.workers.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def notify_new_lead(
    self,
    lead_id: str,
    email: str,
) -> None:
    logger.info(
        "New lead notification queued: lead_id=%s email=%s",
        UUID(lead_id),
        email,
    )
