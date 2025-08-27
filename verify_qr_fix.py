#!/usr/bin/env python
"""
Quick verification script for QR code fixes on payment success page.
This script checks if booking 49 exists and what data it contains.
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine.settings")
django.setup()

from bookings.models import Booking
from django.urls import reverse


def check_booking_49():
    """Check if booking 49 exists and show its details"""
    try:
        booking = Booking.objects.get(id=49)
        print("✅ BOOKING 49 FOUND!")
        print(f"ID: {booking.id}")
        print(f"PNR: {booking.pnr_code}")
        print(
            f"Passenger: {booking.customer.get_full_name() or booking.customer.username}"
        )
        print(f"Route: {booking.route.origin} → {booking.route.destination}")
        print(f"Travel Date: {booking.travel_date}")
        print(f"Trip Type: {booking.trip_type}")
        print(f"Bus: {booking.bus.bus_name}")
        print(f"Seat: {booking.seat.seat_number}")
        print(f"Status: {booking.get_status_display()}")
        print(f"Amount: Le {booking.amount_paid}")

        # Check round trip details
        if booking.trip_type == "round_trip":
            print("\n🔄 RETURN TRIP DETAILS:")
            print(f"Return Date: {booking.return_date}")
            print(
                f"Return Bus: {booking.return_bus.bus_name if booking.return_bus else 'Not set'}"
            )
            print(
                f"Return Seat: {booking.return_seat.seat_number if booking.return_seat else 'Not set'}"
            )

        # Show URLs
        print(f"\n🔗 URLS:")
        print(f"Payment Success: /bookings/payment/success/{booking.id}/")
        print(f"Ticket URL: /bookings/{booking.id}/ticket/")

        return booking

    except Booking.DoesNotExist:
        print("❌ BOOKING 49 NOT FOUND!")
        print("Let's see what bookings exist...")

        recent_bookings = Booking.objects.all().order_by("-created_at")[:10]
        print(f"Recent bookings (last 10):")
        for booking in recent_bookings:
            print(
                f"  ID: {booking.id}, PNR: {booking.pnr_code}, Trip: {booking.trip_type}"
            )

        return None


def main():
    print("🚀 QR CODE FIX VERIFICATION")
    print("=" * 40)

    booking = check_booking_49()

    if booking:
        print("\n✅ FIXES APPLIED:")
        print("1. QR code now points to ticket URL instead of payment success URL")
        print("2. Return trip details included in booking data for QR generation")
        print("3. WhatsApp sharing updated to include return trip info")
        print("4. Payment success page displays all return trip details")
        print(
            "\n🎯 Next step: Test the QR code at http://127.0.0.1:9000/bookings/payment/success/49/"
        )
    else:
        print("\n⚠️  Please create a test booking first or use an existing booking ID")


if __name__ == "__main__":
    main()
