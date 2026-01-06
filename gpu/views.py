from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GPU, Job
from .serializers import GPUSerializer, JobCreateSerializer, JobListSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample


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


@extend_schema(
    tags=["Jobs"],
    summary="Create a job",
    description="Creates a new job for the authenticated user. New jobs start in PENDING status.",
    request=JobCreateSerializer,
    responses={
        201: OpenApiResponse(response=JobCreateSerializer, description="Job created"),
        400: OpenApiResponse(description="Validation error"),
        401: OpenApiResponse(description="Unauthorized"),
    },
    examples=[
        OpenApiExample(
            "Create job request",
            value={"gpu_id": 1, "command": "python train.py"},
            request_only=True,
        ),
        OpenApiExample(
            "Create job response",
            value={
                "id": 12,
                "command": "python train.py",
                "status": "PENDING",
                "tokens_rate": 5,
                "tokens_charged": 0,
                "created_at": "2026-01-07T12:00:00Z",
            },
            response_only=True,
        ),
    ],
)
class JobCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobCreateSerializer


@extend_schema(
    tags=["Jobs"],
    summary="List my jobs",
    description="Returns all jobs created by the authenticated user.",
    responses={200: OpenApiResponse(response=JobListSerializer(many=True))},
)
class MyJobsListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobListSerializer

    def get_queryset(self):
        return (
            Job.objects.filter(user=self.request.user)
            .select_related("gpu")
            .order_by("-created_at")
        )



@extend_schema(
    tags=["Jobs"],
    summary="Run my approved job",
    description="Starts a job owned by the authenticated user if it is APPROVED. "
                "Sets status to RUNNING, creates a JobLog, then Celery starts via the RUNNING signal.",
    responses={
        200: OpenApiResponse(description="Job queued to run"),
        400: OpenApiResponse(description="Job not APPROVED / already running"),
        401: OpenApiResponse(description="Unauthorized"),
        404: OpenApiResponse(description="Job not found"),
    },
)
class RunMyJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk: int):
        job = Job.objects.select_for_update().filter(pk=pk, user=request.user).first()
        if not job:
            return Response({"detail": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

        if job.status == Job.Status.PENDING or job.status == Job.Status.REJECTED:
            return Response(
                {"detail": f"Job should not be pending or rejected to run. Current status: {job.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        job.status = Job.Status.RUNNING
        job.started_at = timezone.now()
        job.save(update_fields=["status", "started_at"])
        job.logs.create(message="Run requested by user; job set to RUNNING.")

        # The signal will enqueue Celery on commit.

        return Response(
            {"id": job.id, "status": job.status, "started_at": job.started_at},
            status=status.HTTP_200_OK,
        )
