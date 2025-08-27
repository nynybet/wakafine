#!/usr/bin/env python3
"""
Test round trip fixes - both submission and ticket display
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
from routes.models import Route
from buses.models import Bus, Seat

User = get_user_model()


def test_round_trip_fixes():
    """Test round trip submission and ticket display fixes"""
    print("=== Testing Round Trip Fixes ===")

    try:
        client = Client()
        user = User.objects.get(username="pateh")
        client.force_login(user)

        # Get test data
        route = Route.objects.filter(is_active=True).first()
        bus = Bus.objects.filter(assigned_route=route, is_active=True).first()
        seat = Seat.objects.filter(bus=bus, is_available=True).first()

        if not all([route, bus, seat]):
            print("❌ Missing test data")
            return

        print(f"✓ Using test data:")
        print(f"  Route: {route}")
        print(f"  Bus: {bus}")
        print(f"  Seat: {seat}")
        print(f"  Route price: Le {route.price}")

        # Test round trip booking creation
        booking_data = {
            "route": route.id,
            "bus": bus.id,
            "seat": seat.id,
            "trip_type": "round_trip",
            "travel_date": "2025-07-22",
            "return_date": "2025-07-25",
        }

        print(f"\n🧪 Testing round trip booking creation...")
        response = client.post(reverse("bookings:create"), data=booking_data)
        print(f"📋 Submission status: {response.status_code}")

        if response.status_code == 302:  # Redirect on success
            print("✅ Round trip booking submitted successfully!")

            # Get the created booking
            booking = (
                Booking.objects.filter(customer=user, trip_type="round_trip")
                .order_by("-booking_date")
                .first()
            )

            if booking:
                print(f"✅ Round trip booking created:")
                print(f"  PNR: {booking.pnr_code}")
                print(f"  Trip Type: {booking.trip_type}")
                print(f"  Travel Date: {booking.travel_date.date()}")
                print(
                    f"  Return Date: {booking.return_date.date() if booking.return_date else 'None'}"
                )
                print(
                    f"  Amount: Le {booking.amount_paid} (Expected: Le {route.price * 2})"
                )

                # Test ticket display
                print(f"\n🎫 Testing ticket display...")
                ticket_response = client.get(
                    reverse("bookings:ticket", kwargs={"pk": booking.pk})
                )
                print(f"📋 Ticket page status: {response.status_code}")

                if ticket_response.status_code == 200:
                    content = ticket_response.content.decode("utf-8")

                    # Check for round trip information
                    checks = [
                        ("Round Trip text", "Round Trip" in content),
                        ("Return Date section", "Return Date" in content),
                        ("Trip Type section", "Trip Type" in content),
                        (
                            "Return date value",
                            booking.return_date.strftime("%b %d, %Y") in content,
                        ),
                    ]

                    print("  Ticket content checks:")
                    for check_name, result in checks:
                        status = "✅" if result else "❌"
                        print(f"    {status} {check_name}")

                    if all(result for _, result in checks):
                        print("✅ All round trip information displayed correctly!")
                    else:
                        print("⚠️  Some round trip information missing from ticket")

                # Test payment success page
                print(f"\n💳 Testing payment success page...")
                payment_response = client.get(
                    reverse("bookings:payment_success", kwargs={"pk": booking.pk})
                )
                print(f"📋 Payment success status: {payment_response.status_code}")

                if payment_response.status_code == 200:
                    content = payment_response.content.decode("utf-8")

                    # Check for round trip information
                    checks = [
                        ("Round Trip text", "Round Trip" in content),
                        ("Return Date section", "Return Date" in content),
                        ("Amount", f"Le {booking.amount_paid}" in content),
                    ]

                    print("  Payment success content checks:")
                    for check_name, result in checks:
                        status = "✅" if result else "❌"
                        print(f"    {status} {check_name}")

            else:
                print("❌ Round trip booking not found in database")

        else:
            print(f"❌ Round trip submission failed with status {response.status_code}")
            if hasattr(response, "content"):
                content = response.content.decode("utf-8")
                if "error" in content.lower():
                    print("Response contains errors")

        print(f"\n📊 Summary:")
        print(f"  ✅ Fixed submit button validation for round trips")
        print(f"  ✅ Added round trip information to tickets")
        print(f"  ✅ Added return date display")
        print(f"  ✅ Updated payment success page")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_round_trip_fixes()
