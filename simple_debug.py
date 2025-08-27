#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine.settings")
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User

print("Starting template debug...")

# Create a test client
client = Client()

# Create a test user or get existing one
try:
    user = User.objects.get(username="testuser")
    print("Found existing test user")
except User.DoesNotExist:
    user = User.objects.create_user(username="testuser", password="testpass123")
    print("Created new test user")

# Login
login_result = client.login(username="testuser", password="testpass123")
print(f"Login successful: {login_result}")

# Make request to the booking page with same parameters
print("Making request to booking page...")
try:
    response = client.get("/bookings/create/?route=1&bus=1")
    print(f"Response status: {response.status_code}")

    # Save response content to a file to examine
    with open("response_debug.html", "w", encoding="utf-8") as f:
        f.write(response.content.decode("utf-8"))
    print("Response content saved to response_debug.html")

    # Check what's in the response content around seats_json
    content = response.content.decode("utf-8")
    if "seats_json" in content:
        print("seats_json found in HTML content")
        # Find the line with seats_json
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "seats_json" in line:
                print(f"Line {i}: {line.strip()}")
    else:
        print("seats_json NOT found in HTML content")

    # Check for seat-map div
    if "seat-map" in content:
        print("seat-map div found in HTML")
    else:
        print("seat-map div NOT found in HTML")

    # Check for JavaScript initialization
    if "Initializing booking form" in content:
        print("JavaScript initialization found")
    else:
        print("JavaScript initialization NOT found")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
