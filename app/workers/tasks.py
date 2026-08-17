from collections.abc import Callable
from typing import Any, cast
from uuid import UUID

from celery import Task
from celery.utils.log import get_task_logger

from app.workers.celery_app import celery_app

logger = get_task_logger(__name__)

celery_task = cast(
    Callable[..., Callable[..., Any]],
    celery_app.task,
)


@celery_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def notify_new_lead(
    self: Task,
    lead_id: str,
    email: str,
) -> None:
    logger.info(
        "New lead notification queued: lead_id=%s email=%s",
        UUID(lead_id),
        email,
    )
