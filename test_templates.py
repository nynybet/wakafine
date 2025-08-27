#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.template.loader import get_template
from django.template import Context
from bookings.models import Booking


def test_templates():
    print("🎫 Testing template syntax...")

    # Get a test booking
    try:
        booking = Booking.objects.get(id=21)
        print(f"✅ Found booking: {booking.pnr_code}")
    except Booking.DoesNotExist:
        print("❌ Booking with ID 21 not found")
        return

    templates_to_test = [
        "bookings/payment_success.html",
        "bookings/ticket.html",
        "bookings/ticket_print.html",
        "bookings/ticket_simple.html",
    ]

    context = {
        "booking": booking,
        "user": booking.customer,
        "qr_data": f"PNR: {booking.pnr_code}",
    }

    for template_name in templates_to_test:
        print(f"\n🔄 Testing template: {template_name}")
        try:
            template = get_template(template_name)
            rendered = template.render(context)
            print(f"✅ Template rendered successfully ({len(rendered)} chars)")
        except Exception as e:
            print(f"❌ Template error: {e}")
            print(f"   Error type: {type(e).__name__}")


if __name__ == "__main__":
    test_templates()
