#!/usr/bin/env python
"""
Simplified test focusing on core booking functionality
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from routes.models import Route
from buses.models import Bus, Seat
from bookings.models import Booking
from django.test import Client
from django.urls import reverse

User = get_user_model()


def test_core_functionality():
    """Test just the core booking functionality"""
    print("TESTING CORE BOOKING FUNCTIONALITY")
    print("=" * 50)

    client = Client()

    # 1. Login
    print("\n1. Testing Login...")
    login_success = client.login(username="customer", password="customer123")
    print(f"Login: {'✅ Success' if login_success else '❌ Failed'}")

    # 2. Check models
    print("\n2. Testing Data Models...")
    routes_count = Route.objects.count()
    buses_count = Bus.objects.count()
    users_count = User.objects.count()
    bookings_count = Booking.objects.count()

    print(f"Routes: {routes_count}")
    print(f"Buses: {buses_count}")
    print(f"Users: {users_count}")
    print(f"Existing Bookings: {bookings_count}")

    # 3. Test direct booking creation
    print("\n3. Testing Direct Booking Creation...")
    try:
        customer = User.objects.get(username="customer")
        test_route = Route.objects.first()
        test_bus = Bus.objects.filter(assigned_route=test_route).first()
        test_seat = test_bus.seats.filter(is_available=True).first()

        new_booking = Booking.objects.create(
            customer=customer,
            route=test_route,
            bus=test_bus,
            seat=test_seat,
            travel_date=timezone.now() + timedelta(days=1),
            payment_method="afrimoney",
            amount_paid=test_route.price,
            status="pending",
        )

        print(f"✅ Booking Created: {new_booking.pnr_code}")
        print(f"   Route: {new_booking.route}")
        print(f"   Bus: {new_booking.bus.bus_name}")
        print(f"   Seat: {new_booking.seat.seat_number}")
        print(f"   QR Code: {'Generated' if new_booking.qr_code else 'Not generated'}")

        # 4. Test basic views
        print("\n4. Testing Views...")

        # Booking list
        list_response = client.get(reverse("bookings:list"))
        print(
            f"Booking List: {'✅ Working' if list_response.status_code == 200 else '❌ Failed'}"
        )

        # Booking search
        search_response = client.get(
            f"/bookings/search/?pnr_code={new_booking.pnr_code}"
        )
        print(
            f"PNR Search: {'✅ Working' if search_response.status_code == 200 else '❌ Failed'}"
        )

        # Payment view
        payment_response = client.get(
            reverse("bookings:payment", kwargs={"pk": new_booking.pk})
        )
        print(
            f"Payment View: {'✅ Working' if payment_response.status_code == 200 else '❌ Failed'}"
        )

        # 5. Test payment simulation
        print("\n5. Testing Payment...")
        payment_post = client.post(
            reverse("bookings:payment", kwargs={"pk": new_booking.pk}),
            {"payment_method": "afrimoney"},
        )
        new_booking.refresh_from_db()
        print(
            f"Payment Status: {'✅ Confirmed' if new_booking.status == 'confirmed' else f'⚠️ {new_booking.status}'}"
        )

        print(f"\n✅ CORE FUNCTIONALITY TEST COMPLETED!")
        print(f"Final booking status: {new_booking.status}")
        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    test_core_functionality()
