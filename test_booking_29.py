#!/usr/bin/env python
"""
Test specific booking and QR code functionality
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from bookings.models import Booking


def test_specific_booking():
    """Test specific booking QR functionality"""
    print("🔍 Testing Booking ID 29 QR Code Functionality")
    print("=" * 50)

    try:
        # Try to get booking with ID 29
        booking = Booking.objects.get(id=29)
        print(f"✅ Found booking: {booking.pnr_code}")
        print(f"   Customer: {booking.customer}")
        print(f"   Status: {booking.status}")
        print(f"   Route: {booking.route}")
        print(f"   Date: {booking.travel_date}")

        # Test client with login
        client = Client()

        # Try to login as the booking owner
        user = booking.customer
        print(f"🔐 Logging in as: {user.username}")

        login_success = client.force_login(user)
        print(
            f"   Login successful: {login_success is None}"
        )  # force_login returns None on success

        # Test print view access
        print("\n🖨️ Testing Print View Access...")
        response = client.get(f"/bookings/{booking.id}/ticket/print/")
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            content = response.content.decode("utf-8")

            # Check for QR code elements
            qr_checks = [
                ("QR Container", 'id="qr-code"' in content),
                ("QR Script", "qrcode.min.js" in content),
                (
                    "Auto-print Script",
                    "auto-print" in content.lower() or "window.print" in content,
                ),
                ("Booking Data", booking.pnr_code in content),
                ("JavaScript QR Generation", "QRCode.toCanvas" in content),
            ]

            print("   QR Code Implementation Checks:")
            for check_name, passed in qr_checks:
                status = "✅" if passed else "❌"
                print(f"     {status} {check_name}")

            # Check for template issues
            if "error" in content.lower() or "exception" in content.lower():
                print("   ⚠️ Possible template errors detected")

            # Save content for debugging
            with open("debug_print_view.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("   💾 Saved page content to debug_print_view.html")

        elif response.status_code == 403:
            print("   ❌ Access forbidden - authentication issue")
        elif response.status_code == 404:
            print("   ❌ Not found - URL or booking issue")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")

        # Test regular ticket view
        print("\n📄 Testing Regular Ticket View...")
        response = client.get(f"/bookings/{booking.id}/ticket/")
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            content = response.content.decode("utf-8")
            print("   ✅ Regular ticket view accessible")

            # Save content for comparison
            with open("debug_ticket_view.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("   💾 Saved page content to debug_ticket_view.html")

        return True

    except Booking.DoesNotExist:
        print("❌ Booking with ID 29 not found")

        # Show available bookings
        bookings = Booking.objects.all()[:5]
        if bookings:
            print("\n📋 Available bookings:")
            for b in bookings:
                print(f"   ID: {b.id}, PNR: {b.pnr_code}, Customer: {b.customer}")
        else:
            print("   No bookings found in database")
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_specific_booking()
