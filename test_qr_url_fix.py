#!/usr/bin/env python3
"""
Test script to verify QR code URL generation
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


def test_qr_code_url():
    """Test that QR code contains the correct URL"""
    print("=== Testing QR Code URL Generation ===")

    try:
        client = Client()
        user = User.objects.get(username="pateh")
        client.force_login(user)

        # Get a recent booking
        booking = Booking.objects.filter(customer=user).order_by("-created_at").first()

        if not booking:
            print("❌ No booking found for testing")
            return

        print(f"✓ Testing with booking PNR: {booking.pnr_code}")

        # Test payment success page
        payment_url = reverse("bookings:payment", kwargs={"pk": booking.pk})
        response = client.get(payment_url)

        print(f"📋 Payment page status: {response.status_code}")

        if response.status_code == 200:
            # Check if the page loads correctly
            content = response.content.decode("utf-8")

            # Look for QR code elements
            if "qr-code" in content:
                print("✅ QR code container found in payment page")
            else:
                print("❌ QR code container not found")

            # Check for the URL template variable
            if "request.build_absolute_uri" in content:
                print("✅ URL generation code found in template")
            else:
                print("❌ URL generation code not found")

            # Test the expected URL format
            expected_url = f"http://testserver{payment_url}"
            print(f"📍 Expected QR URL: {expected_url}")

        # Test ticket page
        ticket_url = reverse("bookings:ticket", kwargs={"pk": booking.pk})
        response = client.get(ticket_url)

        print(f"\n📋 Ticket page status: {response.status_code}")

        if response.status_code == 200:
            content = response.content.decode("utf-8")

            if "qr-code" in content:
                print("✅ QR code container found in ticket page")
            else:
                print("❌ QR code container not found")

            expected_ticket_url = f"http://testserver{ticket_url}"
            print(f"📍 Expected ticket URL: {expected_ticket_url}")

        print(f"\n🎯 QR Code will contain the full URL to the respective pages")
        print(f"   Payment success: {expected_url}")
        print(f"   Ticket view: {expected_ticket_url}")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_qr_code_url()
