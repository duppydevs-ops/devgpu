# jobs/tasks.py
import time
import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction

BILLING_UNIT_SECONDS = 20
logger = logging.getLogger(__name__)


@transaction.atomic
def charge_one_unit_or_stop(job_id: int) -> bool:
    from .models import Job

    job = Job.objects.select_for_update().select_related("user").get(pk=job_id)

    if job.status != Job.Status.RUNNING:
        logger.info("Job %s is not RUNNING, stopping charge loop.", job_id)
        return False

    user = type(job.user).objects.select_for_update().get(pk=job.user_id)

    if user.balance < job.tokens_rate:
        job.status = Job.Status.FAILED
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "finished_at"])
        job.logs.create(message="Stopped: insufficient tokens.")
        logger.warning("Job %s stopped: insufficient tokens.", job_id)
        return False

    user.balance -= job.tokens_rate
    user.save(update_fields=["balance"])

    job.tokens_charged += job.tokens_rate
    job.save(update_fields=["tokens_charged"])
    job.logs.create(message=f"Charged {job.tokens_rate} tokens for {BILLING_UNIT_SECONDS}s unit.")
    logger.info("Job %s charged %s tokens (unit %ss).", job_id, job.tokens_rate, BILLING_UNIT_SECONDS)
    return True


@shared_task
def run_job(job_id: int):
    from .models import Job

    logger.info("Worker received job %s", job_id)

    job = Job.objects.get(pk=job_id)
    if job.status != Job.Status.RUNNING:
        logger.info("Job %s not RUNNING (status=%s). Exiting.", job_id, job.status)
        return

    if not job.started_at:
        job.started_at = timezone.now()
        job.save(update_fields=["started_at"])

    job.logs.create(message="Worker started processing.")
    logger.info("Job %s started processing loop.", job_id)

    while True:
        time.sleep(BILLING_UNIT_SECONDS)
        if not charge_one_unit_or_stop(job_id):
            logger.info("Job %s finished/terminated.", job_id)
            return
