#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from bookings.models import Booking

User = get_user_model()


def test_ticket_views_with_auth():
    print("🎫 Testing ticket views with authentication...")

    # Create test client
    client = Client()

    # Get or create admin user
    admin_user, created = User.objects.get_or_create(
        username="admin",
        defaults={"email": "admin@test.com", "is_staff": True, "is_superuser": True},
    )
    if created:
        admin_user.set_password("admin123")
        admin_user.save()
        print("✅ Created admin user")
    else:
        print("✅ Using existing admin user")

    # Login as admin
    login_success = client.login(username="admin", password="admin123")
    print(f"🔐 Admin login: {'Success' if login_success else 'Failed'}")

    # Get test booking
    try:
        booking = Booking.objects.get(id=21)
        print(f"📝 Testing with booking: {booking.pnr_code}")
    except Booking.DoesNotExist:
        print("❌ Booking with ID 21 not found")
        return

    # Test URLs
    test_urls = [
        f"/bookings/payment/success/{booking.id}/",
        f"/bookings/{booking.id}/ticket/",
        f"/bookings/{booking.id}/ticket/print/",
        f"/bookings/{booking.id}/ticket/pdf/",
    ]

    for url in test_urls:
        print(f"\n🔄 Testing: {url}")
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ SUCCESS - Status: {response.status_code}")
                # Check if it contains expected content
                content = response.content.decode("utf-8")
                if booking.pnr_code in content:
                    print(f"✅ Contains PNR: {booking.pnr_code}")
                else:
                    print(f"⚠️  PNR not found in response")
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                if hasattr(response, "url"):
                    print(f"   Redirect to: {response.url}")
        except Exception as e:
            print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    test_ticket_views_with_auth()
