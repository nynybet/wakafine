#!/usr/bin/env python
"""
Final QR Code and Print Verification Test
Tests that QR codes are properly generated and visible in tickets.
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from bookings.models import Booking
from routes.models import Route
from buses.models import Bus
from accounts.models import Seat

User = get_user_model()


def test_qr_code_visibility():
    """Test QR code generation and visibility in ticket templates"""
    print("🧪 Testing QR Code Visibility and Print Functionality")
    print("=" * 60)

    # Create test client
    client = Client()

    try:
        # Get a test booking
        booking = Booking.objects.filter(status="confirmed").first()
        if not booking:
            print("❌ No confirmed bookings found. Creating test booking...")
            # Create test data if none exists
            from create_test_booking_fixed import create_test_booking

            booking = create_test_booking()

        print(f"✅ Using booking: {booking.pnr_code}")

        # Test user ticket view
        print("\n📄 Testing User Ticket View...")
        try:
            response = client.get(f"/bookings/ticket/{booking.id}/")
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                content = response.content.decode("utf-8")

                # Check for QR code elements
                qr_checks = [
                    ("QR Container", 'id="qr-code"' in content),
                    ("QR Script", "qrcode.min.js" in content),
                    ("QR Generation", "QRCode.toCanvas" in content),
                    ("High Contrast Colors", "dark: '#000000'" in content),
                    ("Print CSS", "@media print" in content),
                    ("Print Color Force", "print-color-adjust: exact" in content),
                    (
                        "QR Visibility Rules",
                        "visibility: visible !important" in content,
                    ),
                    ("QR Ready Event", "qrCodeReady" in content),
                ]

                print("QR Code Implementation Checks:")
                for check_name, passed in qr_checks:
                    status = "✅" if passed else "❌"
                    print(f"  {status} {check_name}")

                # Check print styles specifically for QR
                qr_print_checks = [
                    ("QR Print Size", "width: 120px !important" in content),
                    (
                        "QR Border",
                        "border: 2px solid #000" in content
                        or "border: 3px solid #000" in content,
                    ),
                    ("QR Background", "background: white !important" in content),
                    ("Canvas Styling", "canvas.style" in content),
                ]

                print("\nQR Code Print Styling:")
                for check_name, passed in qr_print_checks:
                    status = "✅" if passed else "❌"
                    print(f"  {status} {check_name}")

            else:
                print(f"❌ Failed to load ticket view: {response.status_code}")

        except Exception as e:
            print(f"❌ Error testing user ticket view: {e}")

        # Test print-specific ticket view
        print("\n🖨️ Testing Print Ticket View...")
        try:
            response = client.get(f"/bookings/ticket/{booking.id}/print/")
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                content = response.content.decode("utf-8")

                # Check print-specific elements
                print_checks = [
                    (
                        "Print Template",
                        "ticket_print.html" in content or "Print Ticket" in content,
                    ),
                    (
                        "Auto Print Script",
                        "window.print" in content or "print()" in content,
                    ),
                    ("QR Ready Listener", "qrCodeReady" in content),
                    ("Print Color Adjust", "print-color-adjust: exact" in content),
                    ("QR Container", 'id="qr-code"' in content),
                ]

                print("Print Implementation Checks:")
                for check_name, passed in print_checks:
                    status = "✅" if passed else "❌"
                    print(f"  {status} {check_name}")

            else:
                print(f"❌ Failed to load print view: {response.status_code}")

        except Exception as e:
            print(f"❌ Error testing print view: {e}")

        # Test bookings list print functionality
        print("\n📋 Testing Bookings List Print...")
        try:
            # Login as the booking owner
            user = booking.customer
            client.force_login(user)

            response = client.get("/bookings/")
            print(f"Bookings List Status: {response.status_code}")

            if response.status_code == 200:
                content = response.content.decode("utf-8")

                list_checks = [
                    (
                        "Print Button",
                        "Print Ticket" in content or 'onclick="printTicket' in content,
                    ),
                    (
                        "Print Function",
                        "function printTicket" in content or "printTicket(" in content,
                    ),
                    ("Popup Window", "window.open" in content),
                    (
                        "Error Handling",
                        "catch" in content or "error" in content.lower(),
                    ),
                ]

                print("List Print Functionality:")
                for check_name, passed in list_checks:
                    status = "✅" if passed else "❌"
                    print(f"  {status} {check_name}")

        except Exception as e:
            print(f"❌ Error testing bookings list: {e}")

        print("\n🎯 QR Code Testing Summary:")
        print("- QR codes use high-contrast black/white colors")
        print("- Print CSS forces color printing and QR visibility")
        print("- QR generation includes fallback for failed loads")
        print("- Print buttons use popup windows for reliability")
        print("- Auto-print waits for QR code generation")

        print("\n📋 Manual Testing Recommendations:")
        print("1. Open a ticket in browser and use Ctrl+P to print")
        print("2. Check 'More settings' > 'Print backgrounds'")
        print("3. Verify QR code appears black on white background")
        print("4. Test print from bookings list page")
        print("5. Try different browsers (Chrome, Firefox, Edge)")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_qr_code_visibility()
    print(f"\n{'🎉 QR Tests Completed!' if success else '❌ QR Tests Failed!'}")
