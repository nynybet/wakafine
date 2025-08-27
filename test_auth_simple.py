#!/usr/bin/env python
import os
import sys
import django

sys.path.append(".")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.test import Client
from accounts.models import User


def test_authenticated_request():
    # Create a session client
    client = Client()

    # Get a test user
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print("No superuser found. Creating one...")
        user = User.objects.create_superuser(
            username="testadmin", email="test@test.com", password="testpass123"
        )

    # Force login
    client.force_login(user)

    # Make request to booking create page
    response = client.get("/bookings/create/?route=1&bus=1")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        content = response.content.decode("utf-8")

        print("HTML Analysis:")
        print(f"- Contains 'seat-map': {'seat-map' in content}")
        print(f"- Contains 'total-price': {'total-price' in content}")
        print(f"- Contains seat CSS class: {'.seat {' in content}")
        print(f"- Contains bookingForm function: {'function bookingForm()' in content}")
        print(
            f"- Contains DOMContentLoaded: {'DOMContentLoaded' in content}"
        )  # Look for JavaScript variables
        print(f"- Contains busId initialization: {'busId:' in content}")
        print(f"- Contains basePrice initialization: {'basePrice:' in content}")
        print(f"- Contains seats JSON check: {'seats_json' in content}")
        print(f"- Contains if seats_json: {'{% if seats_json %}' in content}")
        print(f"- Contains seats assignment: {'this.seats =' in content}")

        # Look for specific seat-related content
        print(f"- Contains renderSeats call: {'this.renderSeats()' in content}")
        print(f"- Contains seat data: {'seat_data' in content}")

        # Search for the actual seats data in various forms
        if "[[" in content:
            print("- Found array-like data in content")
        if '"id":' in content:
            print("- Found JSON-like object in content")
        if "seat_number" in content:
            print("- Found seat_number in content")

        # Extract some key lines for debugging
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "busId:" in line:
                print(f"Line {i}: {line.strip()}")
            if "basePrice:" in line:
                print(f"Line {i}: {line.strip()}")
            if "seats_json" in line and "{% if" in line:
                print(f"Line {i}: {line.strip()}")
                if i + 1 < len(lines):
                    print(f"Line {i+1}: {lines[i+1].strip()}")
                if i + 2 < len(lines):
                    print(f"Line {i+2}: {lines[i+2].strip()}")

        return True
    else:
        print(f"Error: Status {response.status_code}")
        return False


if __name__ == "__main__":
    test_authenticated_request()
