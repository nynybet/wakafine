#!/usr/bin/env python3
"""
Test script to verify the 404 error fix for PaymentView
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine.settings")
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from bookings.models import Booking

User = get_user_model()


def test_404_fix():
    """Test that the 404 error is properly handled"""
    print("=== Testing 404 Error Fix ===")

    client = Client()

    # Test 1: Valid booking for correct user
    try:
        user = User.objects.get(username="pateh")
        print(f"Testing with user: {user.username}")

        # Get a booking for this user
        booking = Booking.objects.filter(customer=user).first()
        if booking:
            client.force_login(user)
            url = reverse("bookings:payment", kwargs={"pk": booking.id})
            response = client.get(url)
            print(
                f"Test 1 - Valid booking: Status {response.status_code} (should be 200)"
            )

    except Exception as e:
        print(f"Test 1 failed: {e}")

    # Test 2: Try to access booking 40 (belongs to another user)
    try:
        user = User.objects.get(username="pateh")
        client.force_login(user)
        url = reverse("bookings:payment", kwargs={"pk": 40})
        response = client.get(url)
        print(
            f"Test 2 - Other user's booking: Status {response.status_code} (should be 302 redirect)"
        )
        if response.status_code == 302:
            print(f"  Redirected to: {response.url}")

    except Exception as e:
        print(f"Test 2 failed: {e}")

    # Test 3: Non-existent booking
    try:
        user = User.objects.get(username="pateh")
        client.force_login(user)
        url = reverse("bookings:payment", kwargs={"pk": 99999})
        response = client.get(url)
        print(
            f"Test 3 - Non-existent booking: Status {response.status_code} (should be 302 redirect)"
        )
        if response.status_code == 302:
            print(f"  Redirected to: {response.url}")

    except Exception as e:
        print(f"Test 3 failed: {e}")


if __name__ == "__main__":
    test_404_fix()
