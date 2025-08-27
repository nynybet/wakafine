from django.db import models
from routes.models import Route


class Bus(models.Model):
    BUS_TYPE_CHOICES = [
        ("mini", "Mini Bus (14 seats)"),
        ("standard", "Standard Bus (25 seats)"),
        ("large", "Large Bus (35 seats)"),
    ]

    bus_number = models.CharField(max_length=20, unique=True)
    bus_name = models.CharField(max_length=100)
    bus_type = models.CharField(
        max_length=20, choices=BUS_TYPE_CHOICES, default="standard"
    )
    seat_capacity = models.PositiveIntegerField()
    assigned_route = models.ForeignKey(
        Route, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.bus_name} ({self.bus_number})"

    @property
    def available_seats(self):
        from bookings.models import Booking
        from django.utils import timezone

        # Get today's bookings for this bus
        today_bookings = Booking.objects.filter(
            bus=self,
            travel_date__date=timezone.now().date(),
            status="confirmed",
        ).count()
        return self.seat_capacity - today_bookings


class Seat(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="seats")
    seat_number = models.CharField(max_length=5)
    is_window = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ["bus", "seat_number"]

    def __str__(self):
        return f"{self.bus.bus_name} - Seat {self.seat_number}"
