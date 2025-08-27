#!/usr/bin/env python3
"""
Simple test to check QR code URL functionality by accessing the actual pages
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


def test_actual_pages():
    """Test actual pages to see QR code content"""
    print("=== Testing Actual QR Code Pages ===")

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

        # Test the correct payment success URL
        payment_success_url = reverse(
            "bookings:payment_success", kwargs={"pk": booking.pk}
        )
        print(f"🔗 Payment success URL: {payment_success_url}")

        response = client.get(payment_success_url)
        print(f"📋 Payment success status: {response.status_code}")

        if response.status_code == 200:
            content = response.content.decode("utf-8")

            # Look for QR code related content
            if "QRCode" in content:
                print("✅ QRCode.js found in payment success page")

            if "ticketUrl" in content:
                print("✅ ticketUrl variable found in payment success page")

                # Extract the URL
                import re

                url_match = re.search(r'ticketUrl\s*=\s*["\']([^"\']+)["\']', content)
                if url_match:
                    url = url_match.group(1)
                    print(f"📍 Extracted ticketUrl: {url}")

            if "qrData = ticketUrl" in content:
                print("✅ QR data is set to ticketUrl")
            elif "qrData" in content:
                qr_match = re.search(r"qrData\s*=\s*([^;]+);", content)
                if qr_match:
                    qr_data = qr_match.group(1).strip()
                    print(f"📍 QR data is set to: {qr_data}")

        # Test ticket page
        ticket_url = reverse("bookings:ticket", kwargs={"pk": booking.pk})
        print(f"\n🔗 Ticket URL: {ticket_url}")

        response = client.get(ticket_url)
        print(f"📋 Ticket status: {response.status_code}")

        if response.status_code == 200:
            content = response.content.decode("utf-8")

            if "QRCode" in content:
                print("✅ QRCode.js found in ticket page")

            # Look for QR data
            import re

            qr_match = re.search(r"qrData\s*=\s*([^;]+);", content)
            if qr_match:
                qr_data = qr_match.group(1).strip()
                print(f"📍 QR data: {qr_data}")
                if "ticketUrl" in qr_data:
                    print("✅ QR data uses ticketUrl variable")
                    # Look for ticketUrl definition
                    url_match = re.search(r"ticketUrl\s*=\s*`([^`]+)`", content)
                    if url_match:
                        url = url_match.group(1)
                        print(f"📍 ticketUrl value: {url}")
                        if "http" in url or ticket_url in url:
                            print("✅ QR data contains proper URL")
                        else:
                            print("⚠️  QR data URL may not be complete")
                elif "http" in qr_data:
                    print("✅ QR data contains HTTP URL")
                else:
                    print("⚠️  QR data does not contain HTTP URL")
            else:
                print("❌ Could not find QR data assignment")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_actual_pages()
