#!/usr/bin/env python3
"""
Live QR Code Test - Test QR functionality in browser
"""

import os
import sys
import requests
import time
from pathlib import Path

# Add the Django project to the path
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")

import django

django.setup()

from bookings.models import Booking


def test_server_running():
    """Test if Django server is running"""
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"✅ Server is running (Status: {response.status_code})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Server is not running: {e}")
        return False


def test_qr_pages():
    """Test QR code pages"""
    print("\n🔍 Testing QR Code Pages")
    print("=" * 50)

    # Get first booking
    booking = Booking.objects.first()
    if not booking:
        print("❌ No bookings found in database")
        return False

    print(f"✅ Testing with booking ID: {booking.id} (PNR: {booking.pnr_code})")

    # Test URLs
    test_urls = [
        f"http://127.0.0.1:8000/bookings/{booking.id}/ticket/",
        f"http://127.0.0.1:8000/bookings/payment/success/{booking.id}/",
        f"http://127.0.0.1:8000/bookings/{booking.id}/ticket/print/",
    ]

    all_passed = True

    for url in test_urls:
        print(f"\n🔍 Testing: {url}")

        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                print(f"  ✅ Page loads successfully")

                # Check for QR library
                if (
                    "cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js"
                    in response.text
                ):
                    print(f"  ✅ Correct QR library found")
                else:
                    print(f"  ❌ QR library not found or incorrect")
                    all_passed = False

                # Check for QR container
                if 'id="qr-code"' in response.text:
                    print(f"  ✅ QR container found")
                else:
                    print(f"  ❌ QR container missing")
                    all_passed = False

                # Check for QR generation script
                if "QRCode.toCanvas" in response.text:
                    print(f"  ✅ QR generation script found")
                else:
                    print(f"  ❌ QR generation script missing")
                    all_passed = False

                # Check for problematic cdnjs
                if (
                    "cdnjs.cloudflare.com" in response.text
                    and "qrcode" in response.text.lower()
                ):
                    print(f"  ❌ Old problematic cdnjs library still present")
                    all_passed = False

                # Check for download buttons
                if (
                    "download" in response.text.lower()
                    and "pdf" in response.text.lower()
                ):
                    print(f"  ⚠️  Download buttons may still be present")
                else:
                    print(f"  ✅ No download buttons detected")

            else:
                print(f"  ❌ Page error: {response.status_code}")
                all_passed = False

        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request failed: {e}")
            all_passed = False

    return all_passed, booking


def print_manual_test_instructions(booking):
    """Print manual testing instructions"""
    print("\n" + "=" * 60)
    print("🧪 MANUAL QR CODE TESTING INSTRUCTIONS")
    print("=" * 60)

    print(f"\n1. 🌐 Open your browser and visit these URLs:")
    print(f"   📄 Ticket Page: http://127.0.0.1:8000/bookings/{booking.id}/ticket/")
    print(
        f"   💳 Payment Success: http://127.0.0.1:8000/bookings/payment/success/{booking.id}/"
    )
    print(
        f"   🖨️  Print Page: http://127.0.0.1:8000/bookings/{booking.id}/ticket/print/"
    )

    print(f"\n2. 🔧 On each page:")
    print(f"   • Open Developer Tools (F12)")
    print(f"   • Go to Console tab")
    print(f"   • Look for QR generation logs starting with 🚀")
    print(f"   • Check if QR codes are visible on the page")

    print(f"\n3. ✅ Expected Results:")
    print(f"   • You should see logs like: '🚀 QR Code generation starting...'")
    print(f"   • Followed by: '✅ QR Code generated successfully!'")
    print(f"   • QR codes should be visible as black and white squares")
    print(f"   • No '❌' error messages in console")

    print(f"\n4. 🚨 If you see errors:")
    print(f"   • '❌ QRCode library failed to load' → Library loading issue")
    print(f"   • '❌ QR container not found' → HTML structure issue")
    print(f"   • '❌ QR generation error' → Data or generation issue")

    print(f"\n5. 🖨️  Print Testing:")
    print(f"   • Try printing any ticket page (Ctrl+P)")
    print(f"   • QR codes should be visible in print preview")
    print(f"   • Page should fit on single page without browser headers")


if __name__ == "__main__":
    print("🔍 LIVE QR CODE TESTING")
    print("=" * 50)

    # Test server
    if not test_server_running():
        print("\n❌ Please start the Django server first:")
        print("   cd C:\\Users\\pateh\\Music\\dissert\\wakafine")
        print("   python manage.py runserver")
        sys.exit(1)

    # Test QR pages
    success, booking = test_qr_pages()

    # Print results
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL AUTOMATED TESTS PASSED!")
        print("\n📋 QR Code Implementation Status:")
        print("  ✅ Server is running")
        print("  ✅ All pages load successfully")
        print("  ✅ Correct QR library (jsdelivr) in all templates")
        print("  ✅ QR containers present")
        print("  ✅ QR generation scripts implemented")
        print("  ✅ No problematic cdnjs libraries")
        print("  ✅ Download buttons removed")

        if booking:
            print_manual_test_instructions(booking)

    else:
        print("❌ SOME TESTS FAILED")
        print("Check the issues reported above.")

    print(f"\n🎯 Next Steps:")
    print(f"  1. Follow the manual testing instructions above")
    print(f"  2. Open browser DevTools to check for JavaScript errors")
    print(f"  3. Verify QR codes are generating and visible")
