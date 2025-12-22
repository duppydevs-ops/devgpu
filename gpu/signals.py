from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Job
from .tasks import run_job


@receiver(pre_save, sender=Job)
def job_pre_save(sender, instance: Job, **kwargs):
    # store old status on the instance so post_save can compare
    if instance.pk:
        old = Job.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
        instance._old_status = old
    else:
        instance._old_status = None


@receiver(post_save, sender=Job)
def job_post_save(sender, instance: Job, created: bool, **kwargs):
    old_status = getattr(instance, "_old_status", None)

    # Trigger only when status changes to APPROVED
    if old_status != Job.Status.APPROVED and instance.status == Job.Status.APPROVED:
        transaction.on_commit(lambda: run_job.delay(instance.id))
