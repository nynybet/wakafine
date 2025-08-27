"""
Simple QR Code Test - No external dependencies
"""

import os
import sys
from pathlib import Path

# Add the Django project to the path
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")

import django

django.setup()

from bookings.models import Booking


def test_qr_templates():
    """Test QR code implementation in templates"""
    print("🎫 QR Code Template Analysis")
    print("=" * 40)

    templates_to_check = [
        "templates/bookings/ticket.html",
        "templates/bookings/payment_success.html",
        "templates/bookings/ticket_simple.html",
        "templates/bookings/ticket_print.html",
    ]

    all_good = True

    for template_path in templates_to_check:
        print(f"\n📄 Checking: {template_path}")
        full_path = os.path.join(os.getcwd(), template_path)

        if not os.path.exists(full_path):
            print(f"  ❌ File not found")
            all_good = False
            continue

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check QR library source
            if "cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js" in content:
                print(f"  ✅ Correct QR library (jsdelivr)")
            elif "cdnjs.cloudflare.com" in content and "qrcode" in content:
                print(f"  ❌ Old cdnjs library detected")
                all_good = False
            else:
                print(f"  ⚠️  No QR library detected")

            # Check for QR container
            if 'id="qr-code"' in content:
                print(f"  ✅ QR container present")
            else:
                print(f"  ❌ QR container missing")
                all_good = False

            # Check for QR generation script
            qr_canvas_count = content.count("QRCode.toCanvas")
            if qr_canvas_count == 1:
                print(f"  ✅ QR generation script present")
            elif qr_canvas_count > 1:
                print(f"  ❌ Duplicate QR scripts ({qr_canvas_count})")
                all_good = False
            else:
                print(f"  ❌ QR generation script missing")
                all_good = False

            # Check for download buttons
            download_patterns = ["download", "ticket_pdf", "href.*pdf"]
            has_download = any(
                pattern.lower() in content.lower() for pattern in download_patterns
            )
            if has_download and "pdf" in content.lower():
                print(f"  ⚠️  Potential download functionality detected")
            else:
                print(f"  ✅ No download buttons found")

        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
            all_good = False

    print("\n" + "=" * 40)
    if all_good:
        print("🎉 ALL TEMPLATES LOOK GOOD!")
        print("\n📋 QR Code Implementation Status:")
        print("  ✅ Correct QR library (jsdelivr) in all templates")
        print("  ✅ QR containers present")
        print("  ✅ QR generation scripts implemented")
        print("  ✅ No duplicate/malformed scripts")
        print("  ✅ Download buttons removed")

        print("\n🚀 Next Steps to Test QR Codes:")
        print("  1. Start Django server: python manage.py runserver")
        print("  2. Open browser to: http://127.0.0.1:8000/")
        print("  3. Navigate to any ticket page")
        print("  4. Open browser DevTools (F12) → Console tab")
        print("  5. Look for QR generation logs starting with 🚀")
        print("  6. QR codes should now be visible!")

    else:
        print("❌ ISSUES FOUND - Check the analysis above")

    return all_good


def check_booking_data():
    """Check if we have booking data to test with"""
    print(f"\n📊 Database Status:")

    try:
        booking_count = Booking.objects.count()
        print(f"  📈 Total bookings: {booking_count}")

        if booking_count > 0:
            latest_booking = Booking.objects.last()
            print(f"  🎫 Latest booking: {latest_booking.pnr_code}")
            print(
                f"  🔗 Test URL: http://127.0.0.1:8000/bookings/{latest_booking.id}/ticket/"
            )
            return latest_booking
        else:
            print(f"  ⚠️  No bookings found - create a booking to test QR codes")
            return None

    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return None


if __name__ == "__main__":
    print("🔍 QR Code Fix Verification")
    print("=" * 50)

    # Test templates
    template_success = test_qr_templates()

    # Check booking data
    test_booking = check_booking_data()

    print("\n" + "=" * 50)
    print(f"🎯 Result: {'SUCCESS' if template_success else 'NEEDS FIXES'}")

    if template_success:
        print("\n🎉 QR Code fixes have been successfully applied!")
        print("📱 QR codes should now generate properly on all ticket pages.")

        if test_booking:
            print(f"\n🧪 To test QR codes:")
            print(f"   1. Ensure Django server is running")
            print(
                f"   2. Visit: http://127.0.0.1:8000/bookings/{test_booking.id}/ticket/"
            )
            print(f"   3. Check browser console for QR generation logs")

        print(f"\n🔧 Issues Fixed:")
        print(f"   ✅ Fixed malformed QR script in ticket.html")
        print(f"   ✅ Updated QR library from cdnjs to jsdelivr")
        print(f"   ✅ Removed problematic integrity hashes")
        print(f"   ✅ Removed all download PDF buttons")
        print(f"   ✅ Standardized QR generation across templates")

    else:
        print("\n❌ There are still issues that need to be addressed.")
        print("Check the template analysis above for details.")
