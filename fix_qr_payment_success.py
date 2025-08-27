#!/usr/bin/env python
"""
Fix QR Code on Payment Success Page with Return Trip Details
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine.settings")
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from bookings.models import Booking
from routes.models import Route
from buses.models import Bus
from django.utils import timezone

User = get_user_model()


def check_current_qr_issue():
    """Check the current state of QR codes and payment success page"""
    print("=== Checking Current QR Code Issue ===\n")

    # Get latest booking
    booking = Booking.objects.last()
    if not booking:
        print("❌ No bookings found. Creating a test booking...")
        return False

    print(f"📋 Latest Booking Details:")
    print(f"   PNR: {booking.pnr_code}")
    print(f"   Trip Type: {booking.trip_type}")
    print(f"   Customer: {booking.customer.username}")
    print(f"   Route: {booking.route}")
    print(f"   Outbound Bus: {booking.bus.bus_name}")
    print(f"   Outbound Seat: {booking.seat.seat_number}")
    print(f"   Travel Date: {booking.travel_date}")

    # Check return trip details
    if booking.trip_type == "round_trip":
        print(f"   🔄 Return Trip Details:")
        print(f"      Return Bus: {booking.return_bus}")
        print(f"      Return Seat: {booking.return_seat}")
        print(f"      Return Date: {booking.return_date}")
    else:
        print(f"   ➡️ One Way Trip")

    # Check payment success URL
    payment_success_url = f"/bookings/payment/success/{booking.pk}/"
    ticket_url = f"/bookings/{booking.pk}/ticket/"

    print(f"\n🔗 URLs:")
    print(f"   Payment Success: http://127.0.0.1:9000{payment_success_url}")
    print(f"   Ticket View: http://127.0.0.1:9000{ticket_url}")

    # Create test client and login
    client = Client()
    client.force_login(booking.customer)

    # Test payment success page
    print(f"\n📄 Testing Payment Success Page...")
    response = client.get(payment_success_url)
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        content = response.content.decode("utf-8")

        # Check for QRCode library
        if "qrcode" in content.lower():
            print("   ✅ QRCode library referenced")
        else:
            print("   ❌ QRCode library NOT found")

        # Check for ticket URL generation
        if "request.build_absolute_uri" in content:
            print("   ✅ Ticket URL generation found")
        else:
            print("   ❌ Ticket URL generation NOT found")

        # Check for return trip details in QR data
        if booking.trip_type == "round_trip":
            if booking.return_seat and str(booking.return_seat.seat_number) in content:
                print("   ✅ Return seat info found in content")
            else:
                print("   ❌ Return seat info NOT found in QR data")

            if booking.return_bus and booking.return_bus.bus_name in content:
                print("   ✅ Return bus info found in content")
            else:
                print("   ❌ Return bus info NOT found in QR data")

            if (
                booking.return_date
                and booking.return_date.strftime("%M d, Y") in content
            ):
                print("   ✅ Return date info found in content")
            else:
                print("   ❌ Return date info NOT found in content")

    return booking


def identify_issues():
    """Identify the specific QR code issues"""
    print("\n=== Identified Issues ===")

    issues = [
        "1. QR code not displaying properly on payment success page",
        "2. QR code missing return trip details (return bus, seat, date)",
        "3. QR code should point to ticket URL with all trip information",
        "4. Return trip details not included in QR data generation",
        "5. JavaScript QR generation missing return trip data",
    ]

    for issue in issues:
        print(f"   ❌ {issue}")

    return issues


def main():
    """Main function to check and identify QR issues"""
    print("🔍 QR Code Payment Success Diagnosis\n")

    # Check current state
    booking = check_current_qr_issue()

    if booking:
        # Identify issues
        identify_issues()

        print(f"\n📋 Summary:")
        print(f"   - Latest booking PNR: {booking.pnr_code}")
        print(f"   - Trip type: {booking.trip_type}")
        print(
            f"   - Payment success URL shows: http://127.0.0.1:9000/bookings/payment/success/{booking.pk}/"
        )
        print(
            f"   - Should show ticket URL instead: http://127.0.0.1:9000/bookings/{booking.pk}/ticket/"
        )

        if booking.trip_type == "round_trip":
            print(f"   - Return details need to be included in QR code")
            print(f"   - Return bus: {booking.return_bus}")
            print(f"   - Return seat: {booking.return_seat}")
            print(f"   - Return date: {booking.return_date}")
    else:
        print("❌ Cannot diagnose without booking data")

    print(f"\n🔧 Next: Update payment success template to fix QR generation")


if __name__ == "__main__":
    main()
