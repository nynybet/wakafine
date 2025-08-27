#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model
from bookings.models import Booking
from django.urls import reverse

User = get_user_model()


def comprehensive_test():
    print("🎫 Comprehensive ticket functionality test...")

    # Setup
    client = Client()

    try:
        admin_user = User.objects.get(username="admin")
        booking = Booking.objects.get(id=21)
        print(f"✅ Admin: {admin_user.username} (staff: {admin_user.is_staff})")
        print(f"✅ Booking: {booking.pnr_code} (customer: {booking.customer.username})")
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return

    # Test 1: Unauthenticated access
    print("\n" + "=" * 50)
    print("🔒 Testing UNAUTHENTICATED access...")

    test_urls = [
        ("payment_success", f"/bookings/payment/success/{booking.id}/"),
        ("ticket", f"/bookings/{booking.id}/ticket/"),
        ("ticket_print", f"/bookings/{booking.id}/ticket/print/"),
        ("ticket_pdf", f"/bookings/{booking.id}/ticket/pdf/"),
    ]

    for name, url in test_urls:
        response = client.get(url)
        print(
            f"📄 {name}: {response.status_code} {'(redirect)' if response.status_code == 302 else ''}"
        )

    # Test 2: Admin authentication
    print("\n" + "=" * 50)
    print("🔐 Testing ADMIN authentication...")

    login_success = client.login(username="admin", password="admin123")
    print(f"Login result: {login_success}")

    if login_success:
        for name, url in test_urls:
            try:
                response = client.get(url)
                print(f"📄 {name}: {response.status_code}")

                if response.status_code == 200:
                    content = response.content.decode("utf-8")
                    has_pnr = booking.pnr_code in content
                    has_qr = "qr-code" in content.lower() or "qrcode" in content.lower()
                    print(f"   ✅ PNR found: {has_pnr}")
                    print(f"   📱 QR elements: {has_qr}")
                elif response.status_code == 302:
                    print(f"   🔄 Redirects to: {response.get('Location', 'unknown')}")
                else:
                    print(f"   ⚠️  Status: {response.status_code}")

            except Exception as e:
                print(f"   ❌ Error: {e}")

    # Test 3: Customer authentication
    print("\n" + "=" * 50)
    print("👤 Testing CUSTOMER authentication...")

    client.logout()
    customer_login = client.login(
        username=booking.customer.username, password="password123"
    )
    print(f"Customer login: {customer_login}")

    if not customer_login:
        # Try with a known password or set one
        customer = booking.customer
        customer.set_password("customer123")
        customer.save()
        customer_login = client.login(
            username=customer.username, password="customer123"
        )
        print(f"Customer login (after password reset): {customer_login}")

    if customer_login:
        for name, url in test_urls:
            try:
                response = client.get(url)
                print(f"📄 {name}: {response.status_code}")

                if response.status_code == 200:
                    content = response.content.decode("utf-8")
                    has_pnr = booking.pnr_code in content
                    print(f"   ✅ PNR found: {has_pnr}")

            except Exception as e:
                print(f"   ❌ Error: {e}")

    print("\n" + "=" * 50)
    print("🎯 Test completed!")


if __name__ == "__main__":
    comprehensive_test()
