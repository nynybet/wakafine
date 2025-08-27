#!/usr/bin/env python3
"""
Quick round trip booking test to debug the issue
"""

import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from bookings.models import Booking
from django.contrib.auth import get_user_model

User = get_user_model()


def check_recent_bookings():
    """Check recent bookings to see if round trip bookings are being created"""

    print("🔍 Checking recent bookings...")

    # Get the most recent bookings
    recent_bookings = Booking.objects.all().order_by("-created_at")[:10]

    print(f"Found {recent_bookings.count()} recent bookings:")

    for booking in recent_bookings:
        print(f"\n📋 Booking PNR: {booking.pnr_code}")
        print(f"   Customer: {booking.customer.username}")
        print(f"   Route: {booking.route}")
        print(f"   Trip Type: {booking.trip_type}")
        print(f"   Outbound Seat: {booking.seat.seat_number}")
        print(
            f"   Return Seat: {booking.return_seat.seat_number if booking.return_seat else 'None'}"
        )
        print(f"   Return Bus: {booking.return_bus if booking.return_bus else 'None'}")
        print(f"   Amount: Le {booking.amount_paid}")
        print(f"   Status: {booking.status}")
        print(f"   Created: {booking.created_at}")

        if booking.is_round_trip:
            print("   ✅ This is a round trip booking")
        else:
            print("   ❌ This is NOT a round trip booking")


if __name__ == "__main__":
    check_recent_bookings()
