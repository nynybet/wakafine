from django.contrib import admin
from .models import Terminal


@admin.register(Terminal)
class TerminalAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "terminal_type",
        "city",
        "location",
        "is_active",
        "operating_hours",
        "created_at",
    ]
    list_filter = ["terminal_type", "city", "is_active", "created_at"]
    search_fields = ["name", "location", "description"]
    list_editable = ["is_active"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Basic Information", {"fields": ("name", "terminal_type", "description")}),
        (
            "Location Details",
            {"fields": ("location", "city", "coordinates_lat", "coordinates_lng")},
        ),
        (
            "Operating Information",
            {
                "fields": (
                    "operating_hours_start",
                    "operating_hours_end",
                    "contact_number",
                )
            },
        ),
        ("Facilities & Status", {"fields": ("facilities", "is_active")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
