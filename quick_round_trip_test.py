#!/usr/bin/env python3
"""
Quick test for round trip booking after fixing the date comparison issue
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from bookings.models import Booking
from django.contrib.auth import get_user_model

User = get_user_model()


def quick_test():
    """Quick test to verify round trip bookings work"""

    print("🧪 Quick Round Trip Test")
    print("=" * 30)

    # Check if there are any recent round trip bookings
    round_trip_bookings = Booking.objects.filter(trip_type="round_trip").order_by(
        "-created_at"
    )[:5]

    print(f"Found {round_trip_bookings.count()} round trip bookings:")

    for booking in round_trip_bookings:
        print(f"\n📋 PNR: {booking.pnr_code}")
        print(f"   Customer: {booking.customer.username}")
        print(f"   Trip Type: {booking.trip_type}")
        print(f"   Is Round Trip: {booking.is_round_trip}")
        print(f"   Outbound Seat: {booking.seat.seat_number}")
        if booking.return_seat:
            print(f"   Return Seat: {booking.return_seat.seat_number}")
        else:
            print("   Return Seat: None")
        if booking.return_bus:
            print(f"   Return Bus: {booking.return_bus.bus_name}")
        else:
            print("   Return Bus: None")
        print(f"   Amount: Le {booking.amount_paid}")
        print(f"   Status: {booking.status}")
        print(f"   Created: {booking.created_at}")


if __name__ == "__main__":
    quick_test()
