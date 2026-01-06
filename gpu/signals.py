from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Job
from .tasks import run_job

@receiver(pre_save, sender=Job)
def job_pre_save(sender, instance: Job, **kwargs):
    if instance.pk:
        instance._old_status = Job.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
    else:
        instance._old_status = None

@receiver(post_save, sender=Job)
def job_post_save(sender, instance: Job, **kwargs):
    old_status = getattr(instance, "_old_status", None)

    if old_status != Job.Status.RUNNING and instance.status == Job.Status.RUNNING:
        # create a log immediately so you can see signal fired
        instance.logs.create(message="Queued to Celery worker.")

        transaction.on_commit(lambda: run_job.delay(instance.id))
