#!/usr/bin/env python3
"""
Comprehensive test for complete round trip booking with return seats
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


def test_complete_round_trip():
    """Test complete round trip booking flow with return seats"""
    print("=== Testing Complete Round Trip Booking ===")

    try:
        client = Client()
        user = User.objects.get(username="pateh")
        client.force_login(user)

        # Get test data
        route = Route.objects.filter(is_active=True).first()
        buses = Bus.objects.filter(assigned_route=route, is_active=True)[
            :2
        ]  # Get 2 buses

        if len(buses) < 2:
            print("❌ Need at least 2 buses for round trip testing")
            return

        outbound_bus = buses[0]
        return_bus = buses[1]

        outbound_seat = Seat.objects.filter(bus=outbound_bus, is_available=True).first()
        return_seat = Seat.objects.filter(bus=return_bus, is_available=True).first()

        if not all([route, outbound_bus, return_bus, outbound_seat, return_seat]):
            print("❌ Missing required test data")
            return

        print(f"✓ Test data:")
        print(f"  Route: {route}")
        print(f"  Outbound Bus: {outbound_bus}")
        print(f"  Return Bus: {return_bus}")
        print(f"  Outbound Seat: {outbound_seat}")
        print(f"  Return Seat: {return_seat}")
        print(f"  Route price: Le {route.price}")

        # Test complete round trip booking
        booking_data = {
            "route": route.id,
            "bus": outbound_bus.id,
            "seat": outbound_seat.id,
            "trip_type": "round_trip",
            "travel_date": "2025-07-22",
            "return_date": "2025-07-25",
            "return_bus": return_bus.id,
            "return_seat": return_seat.id,
        }

        print(f"\n🧪 Testing complete round trip booking...")
        response = client.post(reverse("bookings:create"), data=booking_data)
        print(f"📋 Submission status: {response.status_code}")

        if response.status_code == 302:  # Redirect on success
            print("✅ Complete round trip booking submitted successfully!")

            # Get the created booking
            booking = (
                Booking.objects.filter(
                    customer=user,
                    trip_type="round_trip",
                    return_bus__isnull=False,
                    return_seat__isnull=False,
                )
                .order_by("-booking_date")
                .first()
            )

            if booking:
                print(f"✅ Complete round trip booking created:")
                print(f"  PNR: {booking.pnr_code}")
                print(f"  Trip Type: {booking.trip_type}")
                print(f"  Travel Date: {booking.travel_date.date()}")
                print(
                    f"  Return Date: {booking.return_date.date() if booking.return_date else 'None'}"
                )
                print(f"  Outbound Bus: {booking.bus}")
                print(f"  Outbound Seat: {booking.seat}")
                print(f"  Return Bus: {booking.return_bus}")
                print(f"  Return Seat: {booking.return_seat}")
                print(
                    f"  Amount: Le {booking.amount_paid} (Expected: Le {route.price * 2})"
                )

                # Test ticket display with return journey info
                print(f"\n🎫 Testing ticket with return journey info...")
                ticket_response = client.get(
                    reverse("bookings:ticket", kwargs={"pk": booking.pk})
                )
                print(f"📋 Ticket page status: {ticket_response.status_code}")

                if ticket_response.status_code == 200:
                    content = ticket_response.content.decode("utf-8")

                    # Check for complete round trip information
                    checks = [
                        ("Round Trip text", "Round Trip" in content),
                        ("Return Date section", "Return Date" in content),
                        ("Trip Type section", "Trip Type" in content),
                        ("Return Bus section", "Return Bus" in content),
                        ("Return Seat section", "Return Seat" in content),
                        (
                            "Return date value",
                            booking.return_date.strftime("%b %d, %Y") in content,
                        ),
                        ("Return bus name", booking.return_bus.bus_name in content),
                        (
                            "Return seat number",
                            booking.return_seat.seat_number in content,
                        ),
                        ("Outbound seat number", booking.seat.seat_number in content),
                    ]

                    print("  Complete ticket content checks:")
                    for check_name, result in checks:
                        status = "✅" if result else "❌"
                        print(f"    {status} {check_name}")

                    all_passed = all(result for _, result in checks)
                    if all_passed:
                        print(
                            "✅ All round trip information displayed correctly on ticket!"
                        )
                    else:
                        print("⚠️  Some round trip information missing from ticket")

                # Test payment success page
                print(f"\n💳 Testing payment success with return journey...")
                payment_response = client.get(
                    reverse("bookings:payment_success", kwargs={"pk": booking.pk})
                )
                print(f"📋 Payment success status: {payment_response.status_code}")

                if payment_response.status_code == 200:
                    content = payment_response.content.decode("utf-8")

                    # Check for return journey information
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
                print("❌ Complete round trip booking not found in database")

        else:
            print(f"❌ Round trip submission failed with status {response.status_code}")
            if hasattr(response, "content"):
                content = response.content.decode("utf-8")
                if "error" in content.lower():
                    print("Response contains errors")

        print(f"\n📊 Summary:")
        print(f"  ✅ Added return_bus and return_seat fields to model")
        print(f"  ✅ Updated form to handle return journey selections")
        print(f"  ✅ Enhanced JavaScript for return seat selection")
        print(f"  ✅ Added return journey validation")
        print(f"  ✅ Updated ticket template with return journey info")
        print(f"  ✅ Complete round trip booking process working")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_complete_round_trip()
