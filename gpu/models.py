from django.db import models


class GPU(models.Model):
    vendor = models.CharField(max_length=32)          # e.g. NVIDIA
    name = models.CharField(max_length=64)            # e.g. A100 80GB
    vram_gb = models.PositiveIntegerField()           # e.g. 80

    tokens_per_hour = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.vendor} {self.name} ({self.vram_gb}GB) - {self.tokens_per_hour} tokens/hr"
