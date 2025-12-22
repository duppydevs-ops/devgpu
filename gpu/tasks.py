import time
from celery import shared_task
from django.utils import timezone
from django.db import transaction

BILLING_UNIT_SECONDS = 20

@transaction.atomic
def charge_one_unit_or_stop(job_id):
    from .models import Job
    job = Job.objects.select_for_update().select_related("user").get(pk=job_id)

    if job.status != Job.Status.RUNNING:
        return False

    user = type(job.user).objects.select_for_update().get(pk=job.user_id)

    if user.balance < job.tokens_rate:
        job.status = Job.Status.FAILED
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "finished_at"])
        job.logs.create(message="Stopped: insufficient tokens.")
        return False

    user.balance -= job.tokens_rate
    user.save(update_fields=["balance"])

    job.tokens_charged += job.tokens_rate
    job.save(update_fields=["tokens_charged"])
    job.logs.create(message=f"Charged {job.tokens_rate} tokens for 20s unit.")
    return True


@shared_task
def run_job(job_id: int):
    from .models import Job
    job = Job.objects.get(pk=job_id)

    job.status = Job.Status.RUNNING
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at"])
    job.logs.create(message="Started.")

    while True:
        time.sleep(BILLING_UNIT_SECONDS)

        paid = charge_one_unit_or_stop(job_id)
        if not paid:
            return
