#!/usr/bin/env python3
"""
Test QR Code Functionality
This script tests if QR codes are working in the ticket templates
"""

import requests
import os
import sys

# Add the Django project to the path
sys.path.append("c:/Users/pateh/Music/dissert/wakafine")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine.settings")

import django

django.setup()

from bookings.models import Booking


def test_qr_code_functionality():
    print("🔍 Testing QR Code Functionality...")

    # Test basic server availability
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"✅ Server is running: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not accessible: {e}")
        return False

    # Check if we have any bookings to test with
    try:
        bookings = Booking.objects.all()[:5]
        print(f"📊 Found {len(bookings)} bookings to test")

        if not bookings:
            print("❌ No bookings found to test QR codes")
            return False

        for booking in bookings:
            print(f"\n🎫 Testing Booking #{booking.pk} - PNR: {booking.pnr_code}")

            # Test ticket view
            ticket_url = f"http://127.0.0.1:8000/bookings/{booking.pk}/ticket/"
            try:
                response = requests.get(ticket_url, timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ Ticket page accessible")

                    # Check if QR script is present
                    if "qrcode.min.js" in response.text:
                        print(f"  ✅ QR Code library loaded")
                    else:
                        print(f"  ❌ QR Code library not found")

                    # Check if QR container exists
                    if 'id="qr-code"' in response.text:
                        print(f"  ✅ QR Code container found")
                    else:
                        print(f"  ❌ QR Code container not found")

                    # Check if our QR generation script is present
                    if "QRCode.toCanvas" in response.text:
                        print(f"  ✅ QR Generation script found")
                    else:
                        print(f"  ❌ QR Generation script not found")

                else:
                    print(f"  ❌ Ticket page error: {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"  ❌ Error accessing ticket page: {e}")

            # Test payment success view
            payment_url = (
                f"http://127.0.0.1:8000/bookings/payment/success/{booking.pk}/"
            )
            try:
                response = requests.get(payment_url, timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ Payment success page accessible")

                    # Check if QR script is present
                    if "qrcode.min.js" in response.text:
                        print(f"  ✅ Payment QR Code library loaded")
                    else:
                        print(f"  ❌ Payment QR Code library not found")

                else:
                    print(f"  ❌ Payment success page error: {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"  ❌ Error accessing payment success page: {e}")

            # Only test first booking to avoid spam
            break

        return True

    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def test_qr_debug_page():
    """Test our simple debug page"""
    print("\n🧪 Testing QR Debug Page...")

    debug_url = "file:///c:/Users/pateh/Music/dissert/wakafine/qr_debug_test.html"
    print(
        f"📄 Debug page created at: c:/Users/pateh/Music/dissert/wakafine/qr_debug_test.html"
    )
    print("  ℹ️  Open this file in a browser to test QR code generation manually")


if __name__ == "__main__":
    success = test_qr_code_functionality()
    test_qr_debug_page()

    if success:
        print("\n✅ QR Code tests completed successfully!")
        print("📌 Next steps:")
        print("   1. Open browser and go to http://127.0.0.1:8000/")
        print("   2. Navigate to a booking ticket")
        print("   3. Check browser console for QR generation logs")
        print("   4. Verify QR code displays correctly")
    else:
        print("\n❌ QR Code tests failed - check server and database")
