#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.template.loader import get_template
from bookings.models import Booking


def test_qr_templates():
    print("🎫 Testing QR Code implementation in templates...")

    # Get test booking
    try:
        booking = Booking.objects.get(id=21)
        print(f"✅ Found booking: {booking.pnr_code}")
    except Booking.DoesNotExist:
        print("❌ Booking with ID 21 not found")
        return

    context = {
        "booking": booking,
        "user": booking.customer,
    }

    templates_to_test = [
        "bookings/payment_success.html",
        "bookings/ticket.html",
        "bookings/ticket_print.html",
        "bookings/ticket_simple.html",
    ]

    for template_name in templates_to_test:
        print(f"\n🔄 Testing: {template_name}")
        try:
            template = get_template(template_name)
            rendered = template.render(context)

            # Check for QR code elements
            has_qr_container = 'id="qr-code"' in rendered
            has_qr_script = "QRCode" in rendered
            has_qr_library = "qrcode" in rendered.lower()
            has_proper_escaping = "escapejs" in rendered

            print(f"✅ Template rendered ({len(rendered)} chars)")
            print(f"   📱 QR Container: {'✅' if has_qr_container else '❌'}")
            print(f"   📚 QR Library: {'✅' if has_qr_library else '❌'}")
            print(f"   🔧 QR Script: {'✅' if has_qr_script else '❌'}")
            print(f"   🛡️ Proper Escaping: {'✅' if has_proper_escaping else '❌'}")

            # Check for common issues
            if "undefined" in rendered.lower():
                print("   ⚠️  Warning: 'undefined' found in template")
            if "null" in rendered.lower():
                print("   ⚠️  Warning: 'null' found in template")

        except Exception as e:
            print(f"❌ Template error: {e}")

    print(f"\n🎯 QR Code testing complete!")
    print(f"📝 Manual testing URLs (with Django server running):")
    print(f"   http://127.0.0.1:8000/bookings/payment/success/{booking.id}/")
    print(f"   http://127.0.0.1:8000/bookings/{booking.id}/ticket/")
    print(f"   http://127.0.0.1:8000/bookings/{booking.id}/ticket/print/")


if __name__ == "__main__":
    test_qr_templates()
