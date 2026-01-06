from rest_framework import serializers
from .models import GPU, Job

class GPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPU
        fields = ("id", "vendor", "name", "vram_gb", "tokens_per_hour", "is_active")


class JobCreateSerializer(serializers.ModelSerializer):
    gpu_id = serializers.PrimaryKeyRelatedField(
        source="gpu",
        queryset=GPU.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Job
        fields = ("id", "gpu_id", "command", "status", "tokens_rate", "tokens_charged", "created_at")
        read_only_fields = ("id", "status", "tokens_rate", "tokens_charged", "created_at")

    def validate(self, attrs):
        gpu = attrs["gpu"]
        if not gpu.is_active:
            raise serializers.ValidationError({"gpu_id": "This GPU is not available."})
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        gpu = validated_data["gpu"]

        return Job.objects.create(
            user=request.user,
            gpu=gpu,
            command=validated_data["command"],
            status=Job.Status.PENDING,
            tokens_rate=gpu.tokens_per_hour,  # snapshot price into job
        )


class JobListSerializer(serializers.ModelSerializer):
    gpu_name = serializers.CharField(source="gpu.name", read_only=True)
    gpu_vendor = serializers.CharField(source="gpu.vendor", read_only=True)
    gpu_vram_gb = serializers.IntegerField(source="gpu.vram_gb", read_only=True)

    class Meta:
        model = Job
        fields = (
            "id",
            "gpu_vendor",
            "gpu_name",
            "gpu_vram_gb",
            "command",
            "status",
            "tokens_rate",
            "tokens_charged",
            "created_at",
            "started_at",
            "finished_at",
        )
