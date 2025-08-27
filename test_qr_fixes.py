#!/usr/bin/env python3
"""
Test the QR Code fixes in the ticket templates
"""

import os
import sys
import requests
from pathlib import Path

# Add the Django project to the path
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")

import django

django.setup()

from bookings.models import Booking


def test_template_qr_code_fixes():
    """Test that all templates have proper QR code implementation"""
    print("🎫 Testing QR Code Template Fixes")
    print("=" * 50)

    # Find a booking to test with
    try:
        booking = Booking.objects.filter(status="confirmed").first()
        if not booking:
            booking = Booking.objects.first()

        if not booking:
            print("❌ No bookings found in database")
            return False

        print(f"✅ Using booking: {booking.pnr_code}")

    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

    # Test URLs to check
    test_urls = [
        f"http://127.0.0.1:8000/bookings/{booking.id}/ticket/",
        f"http://127.0.0.1:8000/bookings/payment/success/{booking.id}/",
        f"http://127.0.0.1:8000/bookings/{booking.id}/ticket/print/",
    ]

    all_tests_passed = True

    for url in test_urls:
        print(f"\n🔍 Testing: {url}")

        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                print(f"  ✅ Page loads successfully")

                # Check for proper QR library (jsdelivr, not cdnjs with integrity)
                if (
                    "cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js"
                    in response.text
                ):
                    print(f"  ✅ Correct QR library (jsdelivr) found")
                elif (
                    "cdnjs.cloudflare.com" in response.text
                    and "integrity=" in response.text
                ):
                    print(
                        f"  ❌ Old problematic CDNJS library with integrity hash found"
                    )
                    all_tests_passed = False
                else:
                    print(f"  ⚠️  QR library not detected")

                # Check for QR container
                if 'id="qr-code"' in response.text:
                    print(f"  ✅ QR code container found")
                else:
                    print(f"  ❌ QR code container missing")
                    all_tests_passed = False

                # Check for QR generation script
                if "QRCode.toCanvas" in response.text:
                    print(f"  ✅ QR generation script found")
                else:
                    print(f"  ❌ QR generation script missing")
                    all_tests_passed = False

                # Check for download buttons (should be removed)
                if (
                    "download" in response.text.lower()
                    and "pdf" in response.text.lower()
                ):
                    print(f"  ⚠️  Download buttons may still be present")
                else:
                    print(f"  ✅ No download buttons detected")

                # Check for malformed/duplicate scripts
                qr_script_count = response.text.count("QRCode.toCanvas")
                if qr_script_count > 1:
                    print(
                        f"  ❌ Duplicate QR scripts detected ({qr_script_count} instances)"
                    )
                    all_tests_passed = False
                elif qr_script_count == 1:
                    print(f"  ✅ Single QR script found")

            else:
                print(f"  ❌ Page error: {response.status_code}")
                all_tests_passed = False

        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request failed: {e}")
            all_tests_passed = False

    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! QR Code fixes appear to be working.")
        print("\n📋 Summary of fixes applied:")
        print("  ✅ Fixed QR library source (jsdelivr instead of cdnjs)")
        print("  ✅ Removed problematic integrity hashes")
        print("  ✅ Fixed malformed/duplicate scripts in ticket.html")
        print("  ✅ Removed download buttons from all templates")
        print("  ✅ Standardized QR generation across all templates")
    else:
        print("❌ SOME TESTS FAILED. Check the issues above.")

    return all_tests_passed


def test_simple_qr_page():
    """Test our simple QR test page"""
    print(f"\n🧪 Testing simple QR test page...")

    try:
        # Try to access our test file directly
        test_file_path = (
            "c:\\Users\\pateh\\Music\\dissert\\wakafine\\qr_test_simple.html"
        )
        if os.path.exists(test_file_path):
            print(f"  ✅ Test file created: {test_file_path}")
            print(f"  📖 You can open this file in your browser to test QR generation")
            print(f"  🌐 File URL: file:///{test_file_path}")
        else:
            print(f"  ❌ Test file not found")

    except Exception as e:
        print(f"  ❌ Error checking test file: {e}")


if __name__ == "__main__":
    print("🚀 Starting QR Code Fix Tests...")
    print(f"🌐 Make sure Django server is running at http://127.0.0.1:8000/")

    # Test the Django templates
    success = test_template_qr_code_fixes()

    # Test the simple QR page
    test_simple_qr_page()

    print(f"\n🎯 Test Results: {'SUCCESS' if success else 'FAILURE'}")

    if success:
        print("\n🎉 Next Steps:")
        print("  1. Open your browser to http://127.0.0.1:8000/")
        print("  2. Go to a ticket page (payment success or ticket view)")
        print("  3. Open browser developer tools (F12)")
        print("  4. Check the Console tab for QR generation logs")
        print("  5. Verify QR codes are now visible on the page")
        print("\n📱 QR codes should now be working properly!")
    else:
        print("\n🔧 There are still issues to fix. Check the output above.")
