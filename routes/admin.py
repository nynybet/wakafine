from django.contrib import admin
from .models import Route


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "origin",
        "destination",
        "price",
        "departure_time",
        "arrival_time",
        "duration_formatted",
        "is_active",
    )
    list_filter = ("origin", "destination", "is_active", "created_at")
    search_fields = ("name", "origin", "destination")
    list_editable = ("price", "is_active")
    ordering = ("origin", "departure_time")
