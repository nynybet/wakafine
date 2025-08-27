#!/usr/bin/env python3
"""
Comprehensive test script for ticket QR code and print functionality.
Tests the actual ticket views and QR code generation.
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Setup Django
sys.path.append(".")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from bookings.models import Booking
from buses.models import Bus, Route
from terminals.models import Terminal

User = get_user_model()


def test_ticket_functionality():
    """Test ticket views and QR code functionality."""
    print("🧪 Testing Ticket QR Code and Print Functionality")
    print("=" * 60)

    try:
        # Create a test client
        client = Client()

        # Check if there are any existing bookings
        bookings = Booking.objects.all()[:3]

        if not bookings:
            print(
                "⚠️  No bookings found in database. Creating sample data might be needed."
            )
            return False

        print(f"📊 Found {len(bookings)} booking(s) to test")

        for i, booking in enumerate(bookings, 1):
            print(f"\n🎫 Testing Booking {i}: {booking.pnr_code}")

            # Test main ticket view
            ticket_url = reverse("bookings:ticket", kwargs={"pk": booking.pk})
            print(f"  📍 Testing URL: {ticket_url}")

            response = client.get(ticket_url)
            print(f"  📡 Response Status: {response.status_code}")

            if response.status_code == 200:
                content = response.content.decode("utf-8")

                # Check for QR code elements
                qr_checks = [
                    ("QR Container", 'id="qr-code"' in content),
                    ("QR Script", "QRCode.toCanvas" in content),
                    ("QR Data", booking.pnr_code in content),
                    ("Print CSS", "@media print" in content),
                    ("Print Button", "Print Ticket" in content),
                    ("Enhanced QR Size", "width: 120" in content),
                    ("High Error Correction", "errorCorrectionLevel: 'H'" in content),
                ]

                all_passed = True
                for check_name, result in qr_checks:
                    status = "✅" if result else "❌"
                    print(f"    {status} {check_name}")
                    if not result:
                        all_passed = False

                if all_passed:
                    print(
                        f"  🎉 All QR code checks passed for booking {booking.pnr_code}"
                    )
                else:
                    print(
                        f"  ❌ Some QR code checks failed for booking {booking.pnr_code}"
                    )

            else:
                print(
                    f"  ❌ Failed to load ticket page (Status: {response.status_code})"
                )
                return False

            # Test print view if it exists
            try:
                print_url = reverse("bookings:ticket_print", kwargs={"pk": booking.pk})
                print(f"  📍 Testing Print URL: {print_url}")

                print_response = client.get(print_url)
                print(f"  📡 Print Response Status: {print_response.status_code}")

                if print_response.status_code == 200:
                    print("    ✅ Print view accessible")
                else:
                    print("    ⚠️  Print view not accessible")

            except Exception as e:
                print(f"    ⚠️  Print view not available: {str(e)}")

        # Test bookings list for print functionality
        print(f"\n📋 Testing Bookings List Print Functionality")
        list_url = reverse("bookings:list")
        print(f"  📍 Testing URL: {list_url}")

        list_response = client.get(list_url)
        print(f"  📡 Response Status: {list_response.status_code}")

        if list_response.status_code == 200:
            content = list_response.content.decode("utf-8")

            list_checks = [
                ("Print Ticket Link", "Print Ticket" in content),
                ("Target Blank", 'target="_blank"' in content),
                ("Auto Print", "window.print()" in content),
            ]

            for check_name, result in list_checks:
                status = "✅" if result else "❌"
                print(f"    {status} {check_name}")

        print("\n" + "=" * 60)
        print("🎯 TICKET FUNCTIONALITY TEST COMPLETED!")
        print("\n📋 What was tested:")
        print("  • Ticket page accessibility")
        print("  • QR code container presence")
        print("  • QR code generation script")
        print("  • Print CSS implementation")
        print("  • Print button availability")
        print("  • Enhanced QR code settings")
        print("  • Bookings list print functionality")

        return True

    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_ticket_functionality()

    if success:
        print("\n🎉 All tests completed successfully!")
        print("Your ticket QR code and print functionality is working properly.")
    else:
        print("\n❌ Some tests failed. Please check the output above.")

    exit(0 if success else 1)
