#!/usr/bin/env python
"""Test script to verify QR code URL functionality."""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine.settings")
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from bookings.models import Bus, Route, Terminal, Booking
from django.urls import reverse
import re

User = get_user_model()


def test_qr_url_content():
    """Test that QR codes contain URLs in templates."""

    print("=== QR Code URL Test ===")

    # Setup test data
    client = Client()

    # Create or get user
    user, created = User.objects.get_or_create(
        email="test@example.com",
        defaults={
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+23276123456",
        },
    )
    if created:
        user.set_password("testpass123")
        user.save()

    # Login
    client.login(email="test@example.com", password="testpass123")

    # Get a booking
    booking = Booking.objects.filter(customer=user).first()

    if not booking:
        print("No booking found for user. Creating one...")

        # Create necessary data
        origin, _ = Terminal.objects.get_or_create(
            name="Freetown Terminal",
            defaults={"location": "Freetown", "address": "Main St"},
        )
        destination, _ = Terminal.objects.get_or_create(
            name="Bo Terminal", defaults={"location": "Bo", "address": "Bo St"}
        )

        route, _ = Route.objects.get_or_create(
            origin=origin,
            destination=destination,
            defaults={"duration_hours": 4, "distance_km": 200},
        )

        bus = Bus.objects.filter(route=route).first()
        if not bus:
            bus = Bus.objects.create(
                number_plate="SL-001", capacity=40, route=route, bus_type="Standard"
            )

        booking = Booking.objects.create(
            customer=user,
            route=route,
            bus=bus,
            seat_number=1,
            travel_date="2024-12-20",
            departure_time="08:00:00",
            total_amount=50.00,
            payment_status="completed",
        )

    print(f"Testing with booking ID: {booking.id}")

    # Test Payment Success Page
    payment_success_url = reverse("bookings:payment_success", kwargs={"pk": booking.id})
    print(f"Payment success URL: {payment_success_url}")

    response = client.get(payment_success_url)
    print(f"Payment success response status: {response.status_code}")

    if response.status_code == 200:
        content = response.content.decode("utf-8")

        # Check for QR code generation
        if "qrcode" in content.lower():
            print("✓ QR code library found in payment success page")

        # Check for URL in QR data
        if "ticketUrl" in content:
            print("✓ ticketUrl variable found in payment success page")

            # Extract the URL pattern
            url_pattern = re.search(r'const ticketUrl = ["\']([^"\']+)["\']', content)
            if url_pattern:
                extracted_url = url_pattern.group(1)
                print(f"✓ Extracted URL: {extracted_url}")
            else:
                print("! Could not extract URL from ticketUrl variable")

        # Check for QR data assignment
        if "const qrData = ticketUrl" in content:
            print("✓ QR data is set to ticketUrl")
        elif "qrData" in content:
            print("! QR data found but may not be using ticketUrl")
            # Extract qrData assignment
            qr_pattern = re.search(r"const qrData = ([^;]+);", content)
            if qr_pattern:
                qr_data = qr_pattern.group(1).strip()
                print(f"  QR data is set to: {qr_data}")

    else:
        print(f"✗ Payment success page returned status {response.status_code}")

    # Test Ticket Page
    ticket_url = reverse("bookings:ticket", kwargs={"pk": booking.id})
    print(f"\nTicket URL: {ticket_url}")

    response = client.get(ticket_url)
    print(f"Ticket response status: {response.status_code}")

    if response.status_code == 200:
        content = response.content.decode("utf-8")

        # Check for QR code generation
        if "qrcode" in content.lower():
            print("✓ QR code library found in ticket page")

        # Check for URL in QR data
        if "request.build_absolute_uri" in content:
            print("✓ request.build_absolute_uri found in ticket page")

        # Look for QR data assignment
        qr_pattern = re.search(r'const qrData = ["\']([^"\']*)["\']', content)
        if qr_pattern:
            qr_data = qr_pattern.group(1)
            print(f"✓ QR data extracted: {qr_data}")
            if "http" in qr_data:
                print("✓ QR data contains HTTP URL")
            else:
                print("! QR data does not contain HTTP URL")
        else:
            print("! Could not find QR data assignment in ticket page")

    else:
        print(f"✗ Ticket page returned status {response.status_code}")

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_qr_url_content()
