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

# Get different routes and buses
routes = list(Route.objects.all())
buses = list(Bus.objects.all())

print(f"Creating additional test bookings...")
print(f"Available routes: {len(routes)}")
print(f"Available buses: {len(buses)}")

# Create bookings for different routes and dates
for i in range(min(3, len(routes))):
    route = routes[i]
    bus = route.bus_set.first() or buses[0]  # Get bus assigned to this route

    # Get an available seat (use a simple approach)
    seat = bus.seats.first()

    if seat:
        booking = Booking.objects.create(
            customer=customer_user,
            route=route,
            bus=bus,
            seat=seat,
            travel_date=timezone.now() + timedelta(days=i + 2, hours=8 + i),
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
