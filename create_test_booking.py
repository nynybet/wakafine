#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(__file__))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from bookings.models import Booking
from routes.models import Route
from buses.models import Bus
from django.utils import timezone
from datetime import datetime, timedelta
import uuid

# Get the first route and bus
route = Route.objects.first()
bus = Bus.objects.first()

print(f"Creating booking for route: {route}")
print(f"Using bus: {bus}")

# Create a test booking
booking = Booking.objects.create(
    pnr=str(uuid.uuid4())[:8].upper(),
    route=route,
    bus=bus,
    customer_name="John Doe",
    customer_email="john@example.com",
    customer_phone="+23276123456",
    travel_date=timezone.now().date() + timedelta(days=1),
    departure_time=datetime.strptime("08:00", "%H:%M").time(),
    passengers=2,
    selected_seats=["1A", "1B"],
    total_amount=route.price * 2,
    status="confirmed",
)

print(f"Test booking created successfully!")
print(f"PNR: {booking.pnr}")
print(f"ID: {booking.id}")
print(f"Total Amount: Le {booking.total_amount}")
print(f"Travel Date: {booking.travel_date}")
