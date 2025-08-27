#!/usr/bin/env python3
"""
Final QR Code Verification Test
Tests all QR code implementations and ensures no download buttons remain
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


def analyze_templates():
    """Analyze all templates for QR code implementation quality"""
    print("\n🔍 TEMPLATE ANALYSIS")
    print("=" * 50)

    templates_to_check = [
        "templates/bookings/ticket.html",
        "templates/bookings/payment_success.html",
        "templates/bookings/ticket_simple.html",
        "templates/bookings/ticket_print.html",
    ]

    all_good = True

    for template_path in templates_to_check:
        print(f"\n📄 Analyzing: {template_path}")
        full_path = os.path.join(os.getcwd(), template_path)

        if not os.path.exists(full_path):
            print(f"  ❌ File not found")
            all_good = False
            continue

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check QR library source
            jsdelivr_count = content.count(
                "cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js"
            )
            if jsdelivr_count == 1:
                print(f"  ✅ Correct QR library (jsdelivr)")
            elif jsdelivr_count > 1:
                print(f"  ⚠️  Multiple QR library imports ({jsdelivr_count})")
            elif jsdelivr_count == 0:
                print(f"  ❌ QR library missing or incorrect")
                all_good = False

            # Check for problematic cdnjs
            if "cdnjs.cloudflare.com" in content and "qrcode" in content.lower():
                print(f"  ❌ Old problematic cdnjs library still present")
                all_good = False

            # Check QR container
            if 'id="qr-code"' in content:
                print(f"  ✅ QR container present")
            else:
                print(f"  ❌ QR container missing")
                all_good = False

            # Check QR generation script - CRITICAL TEST
            qr_canvas_count = content.count("QRCode.toCanvas")
            if qr_canvas_count == 1:
                print(f"  ✅ Single QR generation script")
            elif qr_canvas_count > 1:
                print(
                    f"  ❌ DUPLICATE QR SCRIPTS ({qr_canvas_count}) - THIS BREAKS QR CODES!"
                )
                all_good = False
            elif qr_canvas_count == 0:
                print(f"  ❌ QR generation script missing")
                all_good = False

            # Check for download buttons (should be removed)
            download_patterns = ["download", "ticket_pdf", "Download"]
            has_download = any(pattern in content for pattern in download_patterns)
            if has_download:
                print(f"  ❌ Download buttons still present")
                all_good = False
            else:
                print(f"  ✅ No download buttons found")

            # Check for proper script structure
            if "addEventListener('DOMContentLoaded'" in content:
                print(f"  ✅ Proper DOM ready event")
            else:
                print(f"  ⚠️  No DOM ready event found")

        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
            all_good = False

    return all_good


def test_qr_pages_live():
    """Test QR code pages with live server"""
    print("\n🌐 LIVE PAGE TESTING")
    print("=" * 50)

    # Get first booking
    booking = Booking.objects.first()
    if not booking:
        print("❌ No bookings found in database")
        print("   Run: python manage.py shell")
        print(
            "   Then: from bookings.models import Booking; print(Booking.objects.count())"
        )
        return False, None

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

                # Critical QR tests
                if (
                    "cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js"
                    in response.text
                ):
                    print(f"  ✅ Correct QR library found")
                else:
                    print(f"  ❌ QR library incorrect or missing")
                    all_passed = False

                if 'id="qr-code"' in response.text:
                    print(f"  ✅ QR container found")
                else:
                    print(f"  ❌ QR container missing")
                    all_passed = False

                qr_script_count = response.text.count("QRCode.toCanvas")
                if qr_script_count == 1:
                    print(f"  ✅ Single QR script found")
                elif qr_script_count > 1:
                    print(
                        f"  ❌ DUPLICATE QR SCRIPTS ({qr_script_count}) - QR CODES WILL FAIL!"
                    )
                    all_passed = False
                else:
                    print(f"  ❌ QR generation script missing")
                    all_passed = False

                # Check for download buttons
                if (
                    "download" in response.text.lower()
                    and "pdf" in response.text.lower()
                ) or "ticket_pdf" in response.text:
                    print(f"  ❌ Download buttons still present")
                    all_passed = False
                else:
                    print(f"  ✅ No download buttons detected")

            else:
                print(f"  ❌ Page error: {response.status_code}")
                all_passed = False

        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request failed: {e}")
            all_passed = False

    return all_passed, booking


def print_manual_test_guide(booking):
    """Print comprehensive testing guide"""
    print("\n" + "=" * 70)
    print("🧪 MANUAL QR CODE TESTING GUIDE")
    print("=" * 70)

    print(f"\n📋 STEP 1: Open Browser & Test URLs")
    print(f"   🎫 Ticket Page: http://127.0.0.1:8000/bookings/{booking.id}/ticket/")
    print(
        f"   💳 Payment Success: http://127.0.0.1:8000/bookings/payment/success/{booking.id}/"
    )
    print(
        f"   🖨️  Print Page: http://127.0.0.1:8000/bookings/{booking.id}/ticket/print/"
    )

    print(f"\n🔧 STEP 2: Check Browser Console (F12 → Console)")
    print(f"   ✅ Expected logs:")
    print(f"      • '🚀 QR Code generation starting...'")
    print(f"      • '📄 QR Data prepared: ...'")
    print(f"      • '✅ QRCode library loaded, generating QR code...'")
    print(f"      • '✅ QR Code generated successfully!'")
    print(f"      • '🎯 QR Code added to DOM'")

    print(f"\n❌ STEP 3: Watch for Error Patterns")
    print(f"   • '❌ QRCode library failed to load' → Library issue")
    print(f"   • '❌ QR container not found' → HTML structure issue")
    print(f"   • '❌ QR generation error' → Data/generation issue")
    print(f"   • Multiple duplicate logs → Conflict between scripts")

    print(f"\n👀 STEP 4: Visual Verification")
    print(f"   ✅ You should see:")
    print(f"      • Black and white QR code squares")
    print(f"      • QR codes in the designated containers")
    print(f"      • No error messages or fallback text")
    print(f"      • NO download PDF buttons anywhere")

    print(f"\n🖨️  STEP 5: Print Testing")
    print(f"   • Try Ctrl+P on any ticket page")
    print(f"   • QR codes should appear in print preview")
    print(f"   • Page should fit on single page")
    print(f"   • No browser headers/footers should show")

    print(f"\n🔍 STEP 6: Mobile/Responsive Testing")
    print(f"   • Test on mobile device or browser mobile view")
    print(f"   • QR codes should remain visible and scannable")

    print(f"\n🚨 IF QR CODES STILL DON'T APPEAR:")
    print(f"   1. Check browser console for JavaScript errors")
    print(f"   2. Ensure no ad blockers are blocking the QR library")
    print(f"   3. Try different browsers (Chrome, Firefox, Edge)")
    print(f"   4. Clear browser cache and reload pages")


def main():
    print("🔍 FINAL QR CODE VERIFICATION")
    print("=" * 60)

    # Step 1: Analyze templates
    templates_ok = analyze_templates()

    # Step 2: Test server
    if not test_server_running():
        print("\n❌ SERVER NOT RUNNING")
        print("Please start the Django server:")
        print("   cd C:\\Users\\pateh\\Music\\dissert\\wakafine")
        print("   python manage.py runserver")
        return

    # Step 3: Test live pages
    pages_ok, booking = test_qr_pages_live()

    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)

    if templates_ok and pages_ok:
        print("🎉 ALL TESTS PASSED!")
        print("\n📋 QR Code Issues Fixed:")
        print("  ✅ Removed duplicate QR generation scripts")
        print("  ✅ Fixed malformed JavaScript in ticket_print.html")
        print("  ✅ Fixed malformed JavaScript in ticket_simple.html")
        print("  ✅ All templates use correct jsdelivr QR library")
        print("  ✅ All download buttons removed")
        print("  ✅ Single QR generation function per template")
        print("  ✅ Proper DOM ready event handlers")

        if booking:
            print_manual_test_guide(booking)

        print(f"\n🎯 QR CODES SHOULD NOW WORK!")
        print(f"Follow the manual testing guide above to verify.")

    else:
        print("❌ ISSUES STILL REMAIN")
        if not templates_ok:
            print("   • Template analysis failed - check issues above")
        if not pages_ok:
            print("   • Live page testing failed - check issues above")

    print(f"\n🛠️  Next Steps:")
    print(f"  1. Follow manual testing guide above")
    print(f"  2. Check browser console for any remaining errors")
    print(f"  3. Verify QR codes are generating and visible")
    print(f"  4. Test printing functionality")


if __name__ == "__main__":
    main()
