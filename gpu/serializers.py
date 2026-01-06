from rest_framework import serializers
from .models import GPU

class GPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPU
        fields = ("id", "vendor", "name", "vram_gb", "tokens_per_hour", "is_active")
