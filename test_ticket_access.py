#!/usr/bin/env python3
"""
Simple ticket test for round trip booking
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from bookings.models import Booking

User = get_user_model()


def test_ticket_page():
    """Test ticket page access and content"""
    try:
        client = Client()
        user = User.objects.get(username="pateh")
        client.force_login(user)

        # Get the latest round trip booking
        booking = Booking.objects.filter(trip_type="round_trip").last()
        print(f"Testing ticket for booking ID: {booking.id}, PNR: {booking.pnr_code}")

        # Test direct ticket access
        ticket_url = f"/bookings/{booking.id}/ticket/"
        print(f"Testing URL: {ticket_url}")

        response = client.get(ticket_url)
        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            content = response.content.decode("utf-8")
            print("✅ Ticket page loaded successfully")

            # Check for specific content
            checks = [
                ("Round Trip text", "Round Trip" in content),
                ("Return Date text", "Return Date" in content),
                ("Trip Type text", "Trip Type" in content),
                ("PNR Code", booking.pnr_code in content),
                ("Travel Date", "Jul 22, 2025" in content),
                ("Return Date value", "Jul 25, 2025" in content),
            ]

            print("\nContent checks:")
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"  {status} {check_name}")

            # Show relevant snippets
            if "Trip Type" in content:
                print("\n📄 Trip Type section found in content")
            if "Return Date" in content:
                print("📄 Return Date section found in content")

        else:
            print(f"❌ Failed to load ticket page: {response.status_code}")
            if response.status_code == 302:
                print(
                    f"Redirect location: {response.get('Location', 'No location header')}"
                )

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_ticket_page()
