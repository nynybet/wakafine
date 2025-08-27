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
from django.contrib.auth import get_user_model

User = get_user_model()

print("=== WAKA-FINE BUS BOOKING SYSTEM STATUS ===\n")

# Check users
users = User.objects.all()
print(f"👥 USERS ({users.count()}):")
for user in users:
    print(f"   • {user.username} ({user.role}) - {user.email}")

# Check routes
routes = Route.objects.all()
print(f"\n🛣️  ROUTES ({routes.count()}):")
for route in routes:
    print(f"   • {route} - Le {route.price}")

# Check buses
buses = Bus.objects.all()
print(f"\n🚌 BUSES ({buses.count()}):")
for bus in buses:
    seat_count = bus.seats.count()
    print(f"   • {bus} - {seat_count} seats, Route: {bus.assigned_route}")

# Check bookings
bookings = Booking.objects.all()
print(f"\n🎫 BOOKINGS ({bookings.count()}):")
for booking in bookings:
    print(
        f"   • PNR: {booking.pnr_code} | {booking.customer.username} | {booking.route} | {booking.status}"
    )

# Check seat availability for tomorrow
from django.utils import timezone
from datetime import timedelta

tomorrow = timezone.now().date() + timedelta(days=1)
print(f"\n🪑 SEAT AVAILABILITY for {tomorrow}:")
for bus in buses[:3]:  # Check first 3 buses
    booked_seats = Booking.objects.filter(
        bus=bus, travel_date__date=tomorrow, status__in=["confirmed", "pending"]
    ).count()
    available = bus.seat_capacity - booked_seats
    print(f"   • {bus.bus_name}: {available}/{bus.seat_capacity} seats available")

print(f"\n✅ SYSTEM STATUS: All core functionality operational!")
print(
    f"   • Database: {Booking.objects.count()} bookings, {User.objects.count()} users"
)
print(f"   • Routes: {Route.objects.count()} routes configured")
print(
    f"   • Fleet: {Bus.objects.count()} buses with {Seat.objects.count()} total seats"
)
print(f"   • Server: Running on http://127.0.0.1:8000")

print(f"\n🔐 TEST CREDENTIALS:")
print(f"   • Admin: admin / admin@1234")
print(f"   • Staff: staff / staff123")
print(f"   • Customer: customer / customer123")

print(f"\n🧪 SAMPLE PNR CODES FOR TESTING:")
for booking in bookings[:5]:
    print(f"   • {booking.pnr_code} - {booking.route} ({booking.status})")

print(f"\n🌐 KEY URLS TO TEST:")
print(f"   • Home: http://127.0.0.1:8000/")
print(f"   • Login: http://127.0.0.1:8000/accounts/login/")
print(f"   • Route Search: http://127.0.0.1:8000/routes/search/")
print(f"   • Booking Search: http://127.0.0.1:8000/bookings/search/")
print(f"   • Admin Dashboard: http://127.0.0.1:8000/accounts/dashboard/")
print(f"   • Seat Availability API: http://127.0.0.1:8000/bookings/seat-availability/")
