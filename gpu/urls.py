from django.urls import path
from .views import GPUListView

urlpatterns = [
    path("gpus/", GPUListView.as_view(), name="gpu-list"),
]