from django.contrib import admin
from .models import GPU, Job, JobLog


@admin.register(GPU)
class GPUAdmin(admin.ModelAdmin):
    list_display = ("vendor", "name", "vram_gb", "tokens_per_hour", "is_active")
    list_filter = ("vendor", "is_active")
    search_fields = ("vendor", "name")
    ordering = ("vendor", "name")
    list_editable = ("tokens_per_hour", "is_active")


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "gpu",
        "status",
        "tokens_rate",
        "tokens_charged",
        "created_at",
        "started_at",
        "finished_at",
    )
    list_filter = ("status", "gpu", "created_at")
    search_fields = ("id", "user__email", "user__phone_number", "gpu__name", "gpu__vendor", "command")
    readonly_fields = ("tokens_charged", "created_at", "started_at", "finished_at")

    fieldsets = (
        (None, {"fields": ("user", "gpu", "status")}),
        ("Command", {"fields": ("command",)}),
        ("Tokens", {"fields": ("tokens_rate", "tokens_charged")}),
        ("Timestamps", {"fields": ("created_at", "started_at", "finished_at")}),
    )


@admin.register(JobLog)
class JobLogAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "created_at", "short_message")
    list_filter = ("created_at",)
    search_fields = ("job__id", "message")
    readonly_fields = ("created_at",)

    def short_message(self, obj):
        msg = obj.message or ""
        return (msg[:80] + "…") if len(msg) > 80 else msg

    short_message.short_description = "message"
