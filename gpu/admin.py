from django.contrib import admin
from .models import GPU


@admin.register(GPU)
class GPUAdmin(admin.ModelAdmin):
    list_display = ("vendor", "name", "vram_gb", "tokens_per_hour", "is_active")
    list_filter = ("vendor", "is_active")
    search_fields = ("vendor", "name")
    ordering = ("vendor", "name")
    list_editable = ("tokens_per_hour", "is_active")
