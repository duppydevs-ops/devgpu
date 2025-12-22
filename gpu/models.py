from django.db import models


class GPU(models.Model):
    vendor = models.CharField(max_length=32)          # e.g. NVIDIA
    name = models.CharField(max_length=64)            # e.g. A100 80GB
    vram_gb = models.PositiveIntegerField()           # e.g. 80

    tokens_per_hour = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.vendor} {self.name} ({self.vram_gb}GB) - {self.tokens_per_hour} tokens/hr"


class Job(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        APPROVED = "APPROVED"
        RUNNING = "RUNNING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"
        REJECTED = "REJECTED"

    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name="jobs")
    gpu = models.ForeignKey("GPU", on_delete=models.PROTECT, related_name="jobs")

    command = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)

    tokens_rate = models.PositiveIntegerField()
    tokens_charged = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)


class JobLog(models.Model):
    job = models.ForeignKey("Job", on_delete=models.CASCADE, related_name="logs")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Job#{self.job_id} - {self.created_at:%Y-%m-%d %H:%M}"
