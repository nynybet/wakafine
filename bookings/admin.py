from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "pnr_code",
        "customer",
        "route",
        "bus",
        "seat",
        "travel_date",
        "status",
        "amount_paid",
        "booking_date",
    )
    list_filter = ("status", "payment_method", "travel_date", "booking_date")
    search_fields = ("pnr_code", "customer__username", "customer__email")
    readonly_fields = ("pnr_code", "qr_code", "booking_date")
    list_editable = ("status",)
    ordering = ("-booking_date",)
