#!/usr/bin/env python
import os
import django
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wakafine_bus.settings')
django.setup()

from bookings.models import Bookingython
import os
import django
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wakafine_bus.settings')
django.setup()bin/env python
import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from bookings.models import Booking
from django.contrib.auth import get_user_model
from routes.models import Route
from buses.models import Bus, Seat

User = get_user_model()


def debug_bookings():
    print("=== BOOKING DEBUG INFORMATION ===")

    print("\n1. All Users:")
    users = User.objects.all()
    for user in users:
        print(f"   ID: {user.id}, Username: {user.username}, Email: {user.email}")

    print("\n2. All Bookings:")
    bookings = Booking.objects.all()
    if bookings:
        for booking in bookings:
            customer_name = (
                booking.customer.username if booking.customer else "No customer"
            )
            print(
                f"   ID: {booking.id}, PNR: {booking.pnr_code}, Customer: {customer_name}, Status: {booking.status}"
            )
    else:
        print("   No bookings found in database")

    print("\n3. Routes:")
    routes = Route.objects.all()
    for route in routes[:5]:  # Show first 5 routes
        print(
            f"   ID: {route.id}, {route.origin} → {route.destination}, Price: Le {route.price}"
        )

    print("\n4. Buses:")
    buses = Bus.objects.all()
    for bus in buses[:3]:  # Show first 3 buses
        print(f"   ID: {bus.id}, Name: {bus.bus_name}, Number: {bus.bus_number}")

    # Check if booking ID 40 exists
    print(f"\n5. Checking specific booking ID 40:")
    try:
        booking_40 = Booking.objects.get(id=40)
        customer_name = (
            booking_40.customer.username if booking_40.customer else "No customer"
        )
        print(
            f"   Booking 40 EXISTS: PNR: {booking_40.pnr_code}, Customer: {customer_name}"
        )
    except Booking.DoesNotExist:
        print("   Booking ID 40 does NOT exist")

    # Check if booking ID 42 exists
    print(f"\n6. Checking specific booking ID 42:")
    try:
        booking_42 = Booking.objects.get(id=42)
        customer_name = (
            booking_42.customer.username if booking_42.customer else "No customer"
        )
        print(
            f"   Booking 42 EXISTS: PNR: {booking_42.pnr_code}, Customer: {customer_name}"
        )
    except Booking.DoesNotExist:
        print("   Booking ID 42 does NOT exist")

    return bookings, users


def create_test_booking_if_needed():
    """Create a test booking if no bookings exist"""
    bookings = Booking.objects.all()
    if not bookings:
        print("\n=== CREATING TEST BOOKING ===")

        # Get or create a test user
        user, created = User.objects.get_or_create(
            username="testuser",
            defaults={
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        if created:
            user.set_password("testpass123")
            user.save()
            print(f"Created test user: {user.username}")

        # Get first route and bus
        route = Route.objects.first()
        bus = Bus.objects.first()

        if route and bus:
            # Get first available seat
            seat = bus.seats.first()
            if seat:
                booking = Booking.objects.create(
                    customer=user,
                    route=route,
                    bus=bus,
                    seat=seat,
                    travel_date=timezone.now() + timezone.timedelta(days=1),
                    status="pending",
                    amount_paid=route.price,
                    payment_method="afrimoney",
                )
                print(f"Created test booking: ID {booking.id}, PNR: {booking.pnr_code}")
                return booking
            else:
                print("No seats available for test booking")
        else:
            print("No routes or buses available for test booking")

    return None


if __name__ == "__main__":
    bookings, users = debug_bookings()

    if not bookings:
        create_test_booking_if_needed()
        # Run debug again to show the created booking
        debug_bookings()
