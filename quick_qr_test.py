#!/usr/bin/env python
"""
Quick QR Code Test - Check if booking 29 exists and test the print view
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from bookings.models import Booking
from django.test import Client


def main():
    print("🔍 Quick QR Code Test for Booking ID 29")
    print("=" * 50)

    try:
        # Check if booking 29 exists
        try:
            booking = Booking.objects.get(id=29)
            print(f"✅ Found booking 29: {booking.pnr_code}")
            print(f"   Customer: {booking.customer.username}")
            print(f"   Route: {booking.route.origin} → {booking.route.destination}")
            print(f"   Status: {booking.status}")
        except Booking.DoesNotExist:
            print("❌ Booking 29 not found!")
            # Show available bookings
            bookings = Booking.objects.all()[:10]
            print(f"\n📋 Available bookings ({bookings.count()} total):")
            for b in bookings:
                print(
                    f"   ID: {b.id}, PNR: {b.pnr_code}, Customer: {b.customer.username}"
                )
            return

        # Test the print view URL
        client = Client()

        print(f"\n🖨️ Testing print view: /bookings/{booking.id}/ticket/print/")
        response = client.get(f"/bookings/{booking.id}/ticket/print/")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            content = response.content.decode("utf-8", errors="ignore")

            # Check key elements
            checks = [
                ("Title contains PNR", booking.pnr_code in content),
                ("QR Container present", 'id="qr-code"' in content),
                ("QR Library loaded", "qrcode.min.js" in content),
                ("QR generation script", "QRCode.toCanvas" in content),
                ("Auto-print script", "window.print" in content),
                ("Booking data", "bookingData" in content),
                ("Escape JS filter", "escapejs" in content),
                ("Route origin", booking.route.origin in content),
                ("Route destination", booking.route.destination in content),
            ]

            print("\n   🔍 Page Content Checks:")
            all_passed = True
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"     {status} {check_name}")
                if not passed:
                    all_passed = False

            if all_passed:
                print("\n🎉 All checks passed! QR code should be working.")
            else:
                print("\n⚠️ Some checks failed. There might be issues.")

            # Save debug file
            with open("debug_ticket_print.html", "w", encoding="utf-8") as f:
                f.write(content)
            print(f"\n💾 Saved page content to debug_ticket_print.html for inspection")

        elif response.status_code == 404:
            print("   ❌ Page not found - check URL routing")
        elif response.status_code == 403:
            print("   ❌ Access forbidden - authentication required")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")

        print(
            f"\n🌐 Test URL: http://127.0.0.1:8000/bookings/{booking.id}/ticket/print/?autoprint=true"
        )
        print("💡 Manual test: Open this URL in browser to see if QR code appears")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
