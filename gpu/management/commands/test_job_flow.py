# jobs/management/commands/test_job_flow.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from gpu.models import Job, JobLog, GPU
from gpu.tasks import run_job
import gpu.tasks as tasks_module


class Command(BaseCommand):
    help = "Create a test job, auto-run on APPROVED, and print JobLogs."

    def handle(self, *args, **options):
        # Speed up the test (so you don't wait 20 seconds each unit)
        tasks_module.BILLING_UNIT_SECONDS = 1  # 1 second billing unit for this test

        # Make Celery run tasks immediately in the same process (no broker needed)
        from celery import current_app
        current_app.conf.task_always_eager = True
        current_app.conf.task_eager_propagates = True

        User = get_user_model()

        # Create a test user
        email = "test@example.com"
        user, _ = User.objects.get_or_create(email=email, defaults={"balance": 5})
        # Ensure some balance (tokens)
        user.balance = 5
        user.save(update_fields=["balance"])

        # Create a test GPU (tokens_per_hour is treated as tokens per billing unit in your simplified system)
        gpu, _ = GPU.objects.get_or_create(
            vendor="NVIDIA",
            name="A100",
            vram_gb=80,
            defaults={"tokens_per_hour": 2, "is_active": True},  # rate = 2 tokens per unit
        )
        if gpu.tokens_per_hour != 2:
            gpu.tokens_per_hour = 2
            gpu.save(update_fields=["tokens_per_hour"])

        # Create job (PENDING), then approve it (signal should trigger run_job.delay)
        with transaction.atomic():
            job = Job.objects.create(
                user=user,
                gpu=gpu,
                command="simulate: sleep + charge loop",
                status=Job.Status.PENDING,
                tokens_rate=gpu.tokens_per_hour,  # snapshot from GPU
            )

            # Approve -> should trigger signal -> on_commit -> run_job.delay(job.id)
            job.status = Job.Status.APPROVED
            job.save(update_fields=["status"])

        # Refresh and print results
        job.refresh_from_db()
        logs = JobLog.objects.filter(job=job).order_by("created_at")

        self.stdout.write(self.style.SUCCESS(f"Job #{job.id} status={job.status}"))
        self.stdout.write(self.style.SUCCESS(f"User balance now: {user.__class__.objects.get(pk=user.pk).balance}"))
        self.stdout.write(self.style.SUCCESS(f"Tokens charged: {job.tokens_charged}"))

        self.stdout.write("\n--- Job Logs ---")
        if not logs.exists():
            self.stdout.write(self.style.ERROR("No logs found! (Signal/task may not be wired correctly)"))
        else:
            for log in logs:
                self.stdout.write(f"[{log.created_at:%Y-%m-%d %H:%M:%S}] {log.message}")
