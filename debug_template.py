#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine.settings")
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User
from django.template import Template, Context

# Create a test client
client = Client()

# Create a test user or get existing one
try:
    user = User.objects.get(username="testuser")
except User.DoesNotExist:
    user = User.objects.create_user(username="testuser", password="testpass123")

# Login
client.login(username="testuser", password="testpass123")

# Make request to the booking page with same parameters
print("Making request to booking page...")
response = client.get("/bookings/create/?route=1&bus=1")

print(f"Response status: {response.status_code}")
print(
    f"Response context keys: {list(response.context.keys()) if response.context else 'No context'}"
)

if response.context:
    print(f"seats_json in context: {'seats_json' in response.context}")
    if "seats_json" in response.context:
        seats_json = response.context["seats_json"]
        print(f"seats_json type: {type(seats_json)}")
        print(f"seats_json length: {len(seats_json) if seats_json else 'None'}")
        print(
            f"seats_json content (first 200 chars): {seats_json[:200] if seats_json else 'None'}"
        )

    print(f"route in context: {'route' in response.context}")
    if "route" in response.context:
        route = response.context["route"]
        print(f"route: {route}")
        print(f"route price: {getattr(route, 'price', 'No price attr')}")

# Test template condition directly
if response.context and "seats_json" in response.context:
    seats_json = response.context["seats_json"]

    # Test the template condition
    template_content = """
    {% if seats_json %}
    SEATS JSON EXISTS: {{ seats_json|length }}
    {% else %}
    NO SEATS JSON
    {% endif %}
    """

    template = Template(template_content)
    context = Context({"seats_json": seats_json})
    result = template.render(context)
    print(f"Template test result: {result.strip()}")
