#!/usr/bin/env python
"""
Test script to create a round trip booking for testing QR code functionality
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine.settings")
django.setup()

from bookings.models import Booking
from routes.models import Route
from buses.models import Bus, Seat
from django.contrib.auth import get_user_model

User = get_user_model()


def create_test_round_trip_booking():
    """Create a test round trip booking for QR testing"""
    try:
        print("🔍 Creating test round trip booking...")

        # Get or create a test user
        user, created = User.objects.get_or_create(
            username="testuser",
            defaults={
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        print(f"👤 User: {user.username} {'(created)' if created else '(existing)'}")

        # Get first available route
        route = Route.objects.filter(is_active=True).first()
        if not route:
            print("❌ No active routes found!")
            return None

        print(f"🛣️ Route: {route.origin} → {route.destination}")

        # Get first available bus for this route
        bus = Bus.objects.filter(route=route).first()
        if not bus:
            print("❌ No buses found for this route!")
            return None

        print(f"🚌 Bus: {bus.bus_name}")

        # Get first available seat
        seat = Seat.objects.filter(bus=bus, is_available=True).first()
        if not seat:
            print("❌ No available seats found!")
            return None

        print(f"💺 Outbound Seat: {seat.seat_number}")

        # Get return seat
        return_seat = (
            Seat.objects.filter(bus=bus, is_available=True).exclude(id=seat.id).first()
        )
        if not return_seat:
            return_seat = seat  # Use same seat if no other available

        print(f"💺 Return Seat: {return_seat.seat_number}")

        # Create round trip booking
        travel_date = datetime.now() + timedelta(days=1)
        return_date = datetime.now() + timedelta(days=3)

        booking = Booking.objects.create(
            customer=user,
            route=route,
            bus=bus,
            seat=seat,
            travel_date=travel_date,
            trip_type="round_trip",
            return_date=return_date,
            return_bus=bus,
            return_seat=return_seat,
            amount_paid=route.price * 2,  # Round trip price
            payment_method="afrimoney",
            status="confirmed",
        )

        print(f"✅ Created round trip booking!")
        print(f"   ID: {booking.id}")
        print(f"   PNR: {booking.pnr_code}")
        print(f"   Trip Type: {booking.trip_type}")
        print(
            f"   Outbound: {booking.travel_date.strftime('%Y-%m-%d %H:%M')} - Seat {booking.seat.seat_number}"
        )
        print(
            f"   Return: {booking.return_date.strftime('%Y-%m-%d %H:%M')} - Seat {booking.return_seat.seat_number}"
        )

        print(f"\n🔗 Test URLs:")
        print(
            f"   Payment Success: http://127.0.0.1:9000/bookings/payment/success/{booking.id}/"
        )
        print(f"   Ticket: http://127.0.0.1:9000/bookings/{booking.id}/ticket/")

        return booking

    except Exception as e:
        print(f"❌ Error creating test booking: {e}")
        return None


def main():
    print("🧪 QR CODE ROUND TRIP TEST")
    print("=" * 40)

    booking = create_test_round_trip_booking()

    if booking:
        print(f"\n✅ SUCCESS! Test the QR code at:")
        print(f"   http://127.0.0.1:9000/bookings/payment/success/{booking.id}/")
        print(f"\nThe QR code should now:")
        print(f"   ✓ Display properly")
        print(f"   ✓ Include return trip details")
        print(f"   ✓ Point to ticket URL")
        print(f"   ✓ Show round trip information")
    else:
        print("\n❌ Failed to create test booking")


if __name__ == "__main__":
    main()
