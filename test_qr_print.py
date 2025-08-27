#!/usr/bin/env python3
"""
Test QR code visibility in print view
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from bookings.models import Booking


def test_print_view():
    """Test that print view renders correctly with QR code"""

    print("🧪 Testing QR code in print view...")

    # Get a sample booking
    try:
        booking = Booking.objects.filter(status="confirmed").first()
        if not booking:
            print("❌ No confirmed bookings found")
            return False

        print(f"✅ Found booking: {booking.pnr_code}")

        # Create test client
        client = Client()

        # Test print view access
        print_url = reverse("bookings:ticket_print", args=[booking.id])
        print(f"🔗 Testing URL: {print_url}")

        response = client.get(print_url)

        if response.status_code == 200:
            print("✅ Print view accessible")

            # Check for QR code elements in response
            content = response.content.decode()

            # Check for essential elements
            checks = [
                ("QR container", 'id="qr-code"' in content),
                ("QR library", "qrcode.min.js" in content),
                ("Booking data", booking.pnr_code in content),
                ("Print CSS", "print-color-adjust: exact" in content),
                ("QR script", "generateQR" in content or "QRCode.toCanvas" in content),
                ("Auto-print", "autoprint" in content),
            ]

            all_passed = True
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"{status} {check_name}: {'PASS' if passed else 'FAIL'}")
                if not passed:
                    all_passed = False

            # Test auto-print URL
            autoprint_url = f"{print_url}?autoprint=true"
            response_autoprint = client.get(autoprint_url)

            if response_autoprint.status_code == 200:
                print("✅ Auto-print URL accessible")
            else:
                print(f"❌ Auto-print URL failed: {response_autoprint.status_code}")
                all_passed = False

            return all_passed

        else:
            print(f"❌ Print view failed: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error testing print view: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Starting QR Print View Test")
    print("=" * 50)

    success = test_print_view()

    print("=" * 50)
    if success:
        print("✅ All QR print view tests passed!")
        print("💡 Navigate to a print URL to manually verify QR code visibility")
    else:
        print("❌ Some tests failed. Check the print template and QR script.")

    return success


if __name__ == "__main__":
    main()
