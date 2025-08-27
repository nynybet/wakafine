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
from buses.models import Seat
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

# Get the first route and bus
route = Route.objects.first()
bus = Bus.objects.first()

print(f"Creating booking for route: {route}")
print(f"Using bus: {bus}")

# Get or create a customer user
customer, created = User.objects.get_or_create(
    username="testcustomer",
    defaults={
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "customer",
    },
)
if created:
    customer.set_password("testpass123")
    customer.save()
    print(f"Created test customer: {customer.username}")

# Get a seat from the bus
seat = bus.seats.first()

if not seat:
    print("No seats available for this bus!")
    sys.exit(1)

print(f"Using seat: {seat.seat_number}")

# Create a test booking using correct model fields
booking = Booking.objects.create(
    customer=customer,
    route=route,
    bus=bus,
    seat=seat,
    travel_date=timezone.now() + timedelta(days=1),
    payment_method="afrimoney",
    amount_paid=route.price,
    status="confirmed",
)

print(f"Test booking created successfully!")
print(f"PNR: {booking.pnr_code}")
print(f"ID: {booking.id}")
print(f"Amount Paid: Le {booking.amount_paid}")
print(f"Travel Date: {booking.travel_date}")
print(f"Customer: {booking.customer.username}")
print(f"Seat: {booking.seat.seat_number}")
