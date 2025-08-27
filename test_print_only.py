#!/usr/bin/env python3
"""
Direct print view QR verification
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


def test_print_view_only():
    """Test only the print view which is our main concern"""

    print("🎯 DIRECT PRINT VIEW QR VERIFICATION")
    print("=" * 50)

    # Get booking for testing
    booking = Booking.objects.filter(status="confirmed").first()
    if not booking:
        print("❌ No confirmed bookings found for testing")
        return False

    print(f"📋 Testing booking: {booking.pnr_code}")
    print(f"   ID: {booking.id}")

    client = Client()

    # Test print view
    print_url = reverse("bookings:ticket_print", args=[booking.id])
    print(f"🔗 Print URL: {print_url}")

    response = client.get(print_url)

    if response.status_code == 200:
        print("✅ Print view accessible")

        content = response.content.decode()

        # Essential QR checks
        checks = [
            ("QR container", 'id="qr-code"' in content),
            ("QR library", "qrcode.min.js" in content),
            ("QR generation", "QRCode.toCanvas" in content),
            ("Booking PNR", booking.pnr_code in content),
            ("Print CSS", "@media print" in content),
            ("Color adjust", "print-color-adjust: exact" in content),
            ("Auto-print", "autoprint" in content),
            ("Fallback", "showFallback" in content),
        ]

        print("\n📊 QR Implementation Checks:")
        all_good = True
        for name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {name}")
            if not passed:
                all_good = False

        # Test auto-print URL
        print(f"\n🔄 Testing auto-print...")
        autoprint_url = f"{print_url}?autoprint=true"
        autoprint_response = client.get(autoprint_url)

        if autoprint_response.status_code == 200:
            print("✅ Auto-print URL works")
        else:
            print(f"❌ Auto-print failed: {autoprint_response.status_code}")
            all_good = False

        if all_good:
            print(f"\n🎉 SUCCESS! Print view fully configured")
            print(f"📱 Print URL: http://localhost:8000{print_url}")
            print(f"🖨️ Auto-print: http://localhost:8000{autoprint_url}")
            print("\n💡 To verify QR code visually:")
            print("   1. python manage.py runserver")
            print("   2. Open the URLs above in browser")
            print("   3. Confirm QR code appears (not just text)")
            print("   4. Test print preview (Ctrl+P)")
            return True
        else:
            print(f"\n⚠️ Some QR elements missing")
            return False

    else:
        print(f"❌ Print view failed: {response.status_code}")
        return False


if __name__ == "__main__":
    test_print_view_only()
