#!/usr/bin/env python
import os
import sys
import django

sys.path.append(".")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.test import Client
from accounts.models import User


def test_booking_page():
    client = Client()
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print("No superuser found!")
        return

    client.force_login(user)
    response = client.get("/bookings/create/?route=1&bus=1")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        # Check context
        context = response.context
        print(f"Route in context: {'route' in context}")
        print(f"Bus in context: {'bus' in context}")
        print(f"Seats in context: {'seats' in context}")
        print(f"Seats JSON in context: {'seats_json' in context}")

        if "route" in context:
            route = context["route"]
            print(f"Route: {route} (Price: {route.price})")

        if "bus" in context:
            bus = context["bus"]
            print(f"Bus: {bus} (Seats: {bus.seats.count()})")

        if "seats" in context:
            seats = context["seats"]
            print(f"Seats data: {len(seats)} seats")
            if seats:
                available = sum(1 for s in seats if s.get("is_available"))
                print(f"Available seats: {available}")

        # Check if HTML contains expected elements
        content = response.content.decode("utf-8")
        print(f"HTML contains 'seat-map': {'seat-map' in content}")
        print(f"HTML contains 'total-price': {'total-price' in content}")
        print(f"HTML contains seat CSS: {'.seat {' in content}")

        # Look for JavaScript initialization
        print(f"HTML contains bookingForm(): {'bookingForm()' in content}")

        return True
    else:
        print(f"Error: {response.content}")
        return False


if __name__ == "__main__":
    test_booking_page()
