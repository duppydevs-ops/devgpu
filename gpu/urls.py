from django.urls import path
from .views import GPUListView, JobCreateView, MyJobsListView, RunMyJobView

urlpatterns = [
    path("gpus/", GPUListView.as_view(), name="gpu-list"),
    path("job/", JobCreateView.as_view(), name="job-create"),
    path("jobs/my/", MyJobsListView.as_view(), name="my-jobs"),
    path("jobs/<int:pk>/run/", RunMyJobView.as_view(), name="job-run"),
]
