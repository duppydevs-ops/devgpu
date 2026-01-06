from rest_framework import generics, permissions
from .models import GPU
from .serializers import GPUSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse


@extend_schema(
    tags=["GPUs"],
    summary="List available GPUs",
    description="Returns all active GPUs that users can choose for running jobs.",
    responses={
        200: OpenApiResponse(response=GPUSerializer(many=True), description="List of active GPUs"),
    },
)
class GPUListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = GPUSerializer

    def get_queryset(self):
        return GPU.objects.filter(is_active=True).order_by("vendor", "name", "vram_gb")
