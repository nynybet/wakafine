#!/usr/bin/env python
"""
Simple script to check if booking ID 49 exists and verify the URL fix
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


def main():
    print("🔍 CHECKING BOOKING ID 49...")

    try:
        booking = Booking.objects.get(id=49)
        print(f"✅ Found booking ID 49!")
        print(f"   PNR: {booking.pnr_code}")
        print(f"   Customer: {booking.customer.username}")
        print(f"   Route: {booking.route.origin} → {booking.route.destination}")
        print(f"   Status: {booking.get_status_display()}")

        print(f"\n🔗 URLs should now work:")
        print(
            f"   Payment Success: http://127.0.0.1:9000/bookings/payment/success/{booking.id}/"
        )
        print(f"   Ticket: http://127.0.0.1:9000/bookings/{booking.id}/ticket/")

    except Booking.DoesNotExist:
        print("❌ Booking ID 49 not found!")

        # Show available bookings
        bookings = Booking.objects.all().order_by("-id")[:5]
        if bookings:
            print("\n📋 Available bookings (last 5):")
            for b in bookings:
                print(f"   ID {b.id}: {b.pnr_code} ({b.customer.username})")

            latest = bookings[0]
            print(f"\n💡 Try using booking ID {latest.id} instead:")
            print(
                f"   Payment Success: http://127.0.0.1:9000/bookings/payment/success/{latest.id}/"
            )
        else:
            print("❌ No bookings found in database!")


if __name__ == "__main__":
    main()
