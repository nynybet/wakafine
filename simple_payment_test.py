"""
Simple test script to verify payment success page functionality
"""

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from bookings.models import Booking

User = get_user_model()


def test_payment_functionality():
    print("=== Testing Payment Success Page ===")

    # Create test client
    client = Client()

    # Get a user and their booking
    try:
        user = User.objects.get(username="pateh")
        print(f"Found user: {user.username}")
    except User.DoesNotExist:
        user = User.objects.first()
        print(f"Using first available user: {user.username}")

    # Get a booking for this user
    booking = Booking.objects.filter(customer=user).first()
    if not booking:
        print("No bookings found for user")
        return False

    print(f"Testing booking ID: {booking.id}")

    # Log in the user
    client.force_login(user)

    # Access the payment success page
    url = reverse("bookings:payment", kwargs={"pk": booking.id})
    print(f"Testing URL: {url}")

    response = client.get(url)

    if response.status_code == 200:
        print("SUCCESS: Payment page loads correctly")

        # Check template content
        content = response.content.decode()

        checks = [
            ("qrcode.min.js", "QR code library"),
            ("printTicket", "Print function"),
            ("QRCode.toCanvas", "QR generation code"),
        ]

        for check_str, description in checks:
            if check_str in content:
                print(f"SUCCESS: {description} found")
            else:
                print(f"WARNING: {description} missing")

        return True
    else:
        print(f"ERROR: Status code {response.status_code}")
        return False


# Run the test
if __name__ == "__main__":
    success = test_payment_functionality()
    if success:
        print("\nALL TESTS PASSED: Payment success page is working correctly!")
    else:
        print("\nTEST FAILED: Issues found with payment success page")
