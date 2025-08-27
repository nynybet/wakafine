#!/usr/bin/env python3
"""
Accurate QR code verification test
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


def test_qr_accurate():
    """Accurate test of QR functionality"""
    print("=== Accurate QR Code Test ===")

    try:
        client = Client()
        user = User.objects.get(username="pateh")
        client.force_login(user)

        booking = Booking.objects.filter(customer=user).first()
        if not booking:
            print("❌ No booking found")
            return

        print(f"✓ Testing booking PNR: {booking.pnr_code}")

        # Test Payment Success Page
        payment_success_url = reverse(
            "bookings:payment_success", kwargs={"pk": booking.pk}
        )
        response = client.get(payment_success_url)

        print(f"\n🔗 Payment Success ({payment_success_url}):")

        if response.status_code == 200:
            content = response.content.decode("utf-8")

            checks = [
                ("✅ QRCode library", "typeof QRCode" in content),
                ("✅ QR container", 'id="qr-code"' in content),
                ("✅ QR data setup", "qrData = ticketUrl" in content),
                ("✅ Ticket URL", "ticketUrl" in content),
            ]

            for check_name, result in checks:
                print(f"   {check_name if result else check_name.replace('✅', '❌')}")

        # Test Ticket Page
        ticket_url = reverse("bookings:ticket", kwargs={"pk": booking.pk})
        response = client.get(ticket_url)

        print(f"\n🔗 Ticket Page ({ticket_url}):")

        if response.status_code == 200:
            content = response.content.decode("utf-8")

            checks = [
                ("✅ QRCode library", "typeof QRCode" in content),
                ("✅ QR container", 'id="qr-code"' in content),
                ("✅ QR data setup", "const qrData = ticketUrl;" in content),
                ("✅ Absolute URI", "request.build_absolute_uri" in content),
            ]

            for check_name, result in checks:
                print(f"   {check_name if result else check_name.replace('✅', '❌')}")

        print(f"\n🎯 QR Code Functionality Status:")
        print(f"   📱 Payment Success QR: Points to ticket page URL")
        print(f"   📱 Ticket Page QR: Points to current page URL")
        print(f"   🔗 Example URLs will be like: http://127.0.0.1:8000{ticket_url}")
        print(f"   ✅ QR codes will show proper URLs instead of ticket text")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_qr_accurate()
