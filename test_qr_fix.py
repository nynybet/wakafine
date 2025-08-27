#!/usr/bin/env python3
"""
Final QR Code Fix Verification
Tests the corrected QR implementation
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
from django.urls import reverse
from bookings.models import Booking


def test_qr_fix():
    """Test the QR code fix"""

    print("🔧 TESTING QR CODE FIX")
    print("=" * 40)

    # Get booking
    booking = Booking.objects.filter(status="confirmed").first()
    if not booking:
        print("❌ No confirmed bookings found")
        return False

    print(f"📋 Testing with booking: {booking.pnr_code}")

    client = Client()

    # Test print view
    print_url = reverse("bookings:ticket_print", args=[booking.id])
    response = client.get(print_url)

    if response.status_code == 200:
        print("✅ Print view accessible")

        content = response.content.decode()

        # Check for the fix - ensure we're using correct QRCode.toCanvas syntax
        qr_syntax_checks = [
            ("Fixed QR syntax", "QRCode.toCanvas(qrData," in content),
            ("No temp div bug", "QRCode.toCanvas(tempDiv," not in content),
            ("QR container", 'id="qr-code"' in content),
            ("QR library", "qrcode.min.js" in content),
            ("Error handling", "showFallback" in content),
        ]

        print("\n🔍 QR Implementation Checks:")
        all_good = True
        for name, passed in qr_syntax_checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {name}")
            if not passed:
                all_good = False

        if all_good:
            print(f"\n🎉 QR CODE FIX APPLIED SUCCESSFULLY!")
            print(f"📱 Test URL: http://localhost:8000{print_url}")
            print(f"🖨️ Auto-print: http://localhost:8000{print_url}?autoprint=true")
            print("\n💡 Key Fix Applied:")
            print("   - Changed QRCode.toCanvas(tempDiv, qrData, ...) ")
            print("   - To: QRCode.toCanvas(qrData, ...)")
            print("   - This was causing QR generation to fail silently")
            print("\n🚀 Next Steps:")
            print("   1. Start server: python manage.py runserver")
            print("   2. Open the URL above")
            print("   3. Verify QR code now appears (not just fallback)")
            return True
        else:
            print(f"\n⚠️ Some issues still remain")
            return False

    else:
        print(f"❌ Print view failed: {response.status_code}")
        return False


if __name__ == "__main__":
    test_qr_fix()
