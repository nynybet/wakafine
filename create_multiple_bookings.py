#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from bookings.models import Booking
from routes.models import Route
from buses.models import Bus, Seat
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

# Get existing users
customer_user = User.objects.get(username="customer")
staff_user = User.objects.get(username="staff")

# Get different routes and buses
routes = list(Route.objects.all())
buses = list(Bus.objects.all())

print(f"Creating additional test bookings...")
print(f"Available routes: {len(routes)}")
print(f"Available buses: {len(buses)}")

# Create bookings for different routes and dates
for i in range(3):
    route = routes[i] if i < len(routes) else routes[0]
    bus = buses[i] if i < len(buses) else buses[0]

    # Get an available seat
    available_seats = bus.seats.filter(
        id__not_in=Booking.objects.filter(
            bus=bus, travel_date__date=timezone.now().date() + timedelta(days=i + 1)
        ).values_list("seat_id", flat=True)
    )

    if available_seats.exists():
        seat = available_seats.first()

        booking = Booking.objects.create(
            customer=customer_user,
            route=route,
            bus=bus,
            seat=seat,
            travel_date=timezone.now() + timedelta(days=i + 1, hours=8 + i),
            payment_method=["afrimoney", "qmoney", "orange_money"][i % 3],
            amount_paid=route.price,
            status="confirmed",
        )

        print(
            f"Created booking {i+1}: PNR {booking.pnr_code} for {route} on {booking.travel_date.date()}"
        )

print("\nAll test bookings created successfully!")
print("\nSummary of all bookings:")
for booking in Booking.objects.all():
    print(
        f"PNR: {booking.pnr_code} | Customer: {booking.customer.username} | Route: {booking.route} | Date: {booking.travel_date.date()}"
    )
