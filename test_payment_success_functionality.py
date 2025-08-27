#!/usr/bin/env python3
"""
Test script to verify payment success page functionality
- QR code generation
- Print functionality
- Proper error handling
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine.settings")
django.setup()

from bookings.models import Booking

User = get_user_model()


def test_payment_success_page():
    """Test that payment success page loads correctly for a valid booking"""
    print("=== Testing Payment Success Page Functionality ===")

    # Create test client
    client = Client()

    # Get a user and their booking
    try:
        user = User.objects.get(username="pateh")
        print(f"Found user: {user.username}")
    except User.DoesNotExist:
        user = User.objects.first()
        print(f"Using first available user: {user.username}")

    # Get a booking that belongs to this user
    try:
        booking = Booking.objects.filter(customer=user).first()
        if not booking:
            print("❌ No bookings found for user")
            return False

        print(f"Found booking: ID {booking.id}")

        # Log in the user
        client.force_login(user)

        # Access the payment success page
        url = reverse("bookings:payment", kwargs={"pk": booking.id})
        print(f"Testing URL: {url}")

        response = client.get(url)

        if response.status_code == 200:
            print("✅ Payment success page loads successfully")

            # Check if booking data is in context
            if "booking" in response.context:
                print("✅ Booking data available in template context")

                # Check if QR code library is included
                content = response.content.decode()
                if "qrcode.min.js" in content:
                    print("✅ QR code library included in template")
                else:
                    print("❌ QR code library missing from template")

                # Check if print function exists
                if "printTicket" in content:
                    print("✅ Print function included in template")
                else:
                    print("❌ Print function missing from template")

                # Check if QR generation code exists
                if "QRCode.toCanvas" in content:
                    print("✅ QR code generation code found")
                else:
                    print("❌ QR code generation code missing")

                return True
            else:
                print("❌ Booking data missing from template context")
                return False

        elif response.status_code == 302:
            print(f"❌ Redirected to: {response.url}")
            return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error testing payment success page: {e}")
        return False


def test_payment_access_control():
    """Test that users can't access other users' bookings"""
    print("\n=== Testing Payment Access Control ===")

    client = Client()

    try:
        # Get two different users
        user1 = User.objects.get(username="pateh")
        user2 = User.objects.exclude(username="pateh").first()

        if not user2:
            print("❌ Need at least 2 users for access control test")
            return False

        print(f"User 1: {user1.username}")
        print(f"User 2: {user2.username}")

        # Get a booking belonging to user2
        booking = Booking.objects.filter(customer=user2).first()
        if not booking:
            print(f"❌ No bookings found for user {user2.username}")
            return False

        print(
            f"Testing access to booking ID {booking.id} (belongs to {user2.username})"
        )

        # Log in as user1 and try to access user2's booking
        client.force_login(user1)

        url = reverse("bookings:payment", kwargs={"pk": booking.id})
        response = client.get(url)

        if response.status_code == 302:
            print("✅ Access denied - user redirected (correct behavior)")
            return True
        elif response.status_code == 404:
            print("✅ Access denied - 404 error (correct behavior)")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print("❌ User was able to access another user's booking")
            return False

    except Exception as e:
        print(f"❌ Error testing access control: {e}")
        return False


if __name__ == "__main__":
    print("Testing Payment Success Page Functionality\n")

    success1 = test_payment_success_page()
    success2 = test_payment_access_control()

    print(f"\n=== Test Results ===")
    print(f"Payment Success Page: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Access Control: {'✅ PASS' if success2 else '❌ FAIL'}")

    if success1 and success2:
        print(
            "\n🎉 All tests passed! Payment success functionality is working correctly."
        )
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
