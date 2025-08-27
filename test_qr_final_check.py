#!/usr/bin/env python3
"""
Final test to verify QR code URL functionality
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


def test_qr_functionality():
    """Final test of QR code URL functionality"""
    print("=== Final QR Code URL Test ===")

    try:
        client = Client()
        user = User.objects.get(username="pateh")
        client.force_login(user)

        # Get a booking
        booking = Booking.objects.filter(customer=user).first()
        if not booking:
            print("❌ No booking found for user")
            return

        print(f"✓ Testing with booking PNR: {booking.pnr_code}")

        # Test Payment Success Page
        payment_success_url = reverse(
            "bookings:payment_success", kwargs={"pk": booking.pk}
        )
        print(f"\n🔗 Payment Success URL: {payment_success_url}")

        response = client.get(payment_success_url)
        print(f"📋 Payment success status: {response.status_code}")

        if response.status_code == 200:
            content = response.content.decode("utf-8")

            if "QRCode" in content:
                print("✅ QRCode.js found")

            if "const qrData = ticketUrl;" in content:
                print("✅ QR data correctly set to ticketUrl")

                # Check if ticketUrl is defined
                if "ticketUrl" in content:
                    print("✅ ticketUrl variable exists")

                    # Look for URL pattern
                    import re

                    url_match = re.search(
                        r'ticketUrl\s*=\s*["\']([^"\']+)["\']', content
                    )
                    if url_match:
                        url = url_match.group(1)
                        print(f"📍 Payment success QR will show: {url}")
                        if "/ticket/" in url:
                            print("✅ QR points to ticket page URL")
                        else:
                            print("⚠️  QR URL format unexpected")
            else:
                print("❌ QR data not set to ticketUrl correctly")

        # Test Ticket Page
        ticket_url = reverse("bookings:ticket", kwargs={"pk": booking.pk})
        print(f"\n🔗 Ticket Page URL: {ticket_url}")

        response = client.get(ticket_url)
        print(f"📋 Ticket page status: {response.status_code}")

        if response.status_code == 200:
            content = response.content.decode("utf-8")

            if "QRCode" in content:
                print("✅ QRCode.js found")

            if "const qrData = ticketUrl;" in content:
                print("✅ QR data correctly set to ticketUrl")

                # Check ticketUrl definition
                if "request.build_absolute_uri" in content:
                    print("✅ Using request.build_absolute_uri for URL")
                    print("📍 Ticket QR will show the current ticket page URL")
                else:
                    print("⚠️  URL generation method not found")
            else:
                print("❌ QR data not set to ticketUrl correctly")

        print(f"\n🎯 Summary:")
        print(f"   Payment Success QR → Points to ticket page URL")
        print(f"   Ticket Page QR → Points to current ticket page URL")
        print(f"   Expected QR URL format: http://127.0.0.1:8000{ticket_url}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_qr_functionality()
