from django.contrib import admin
from .models import Bus, Seat


class SeatInline(admin.TabularInline):
    model = Seat
    extra = 0


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = (
        "bus_name",
        "bus_number",
        "bus_type",
        "seat_capacity",
        "assigned_route",
        "available_seats",
        "is_active",
    )
    list_filter = ("bus_type", "is_active", "assigned_route")
    search_fields = ("bus_name", "bus_number")
    list_editable = ("is_active",)
    inlines = [SeatInline]


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("bus", "seat_number", "is_window", "is_available")
    list_filter = ("bus", "is_window", "is_available")
    search_fields = ("bus__bus_name", "seat_number")
