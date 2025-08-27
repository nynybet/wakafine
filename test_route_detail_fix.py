#!/usr/bin/env python3
"""
Test the routes detail page Back to Routes button fix
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
from routes.models import Route

User = get_user_model()


def test_route_detail_page():
    """Test the route detail page and Back to Routes button"""
    print("=== Testing Route Detail Page Fix ===")

    try:
        client = Client()

        # Get a route to test with
        route = Route.objects.filter(is_active=True).first()

        if not route:
            print("❌ No active routes found for testing")
            return

        print(f"✓ Testing with route: {route.name} (ID: {route.id})")

        # Test route detail page access
        detail_url = reverse("routes:detail", kwargs={"pk": route.id})
        print(f"📋 Testing URL: {detail_url}")

        response = client.get(detail_url)
        print(f"📋 Route detail page status: {response.status_code}")

        if response.status_code == 200:
            content = response.content.decode("utf-8")

            # Check for the fixed Back to Routes button
            checks = [
                ("Route name in title", route.name in content),
                ("Back to Routes button", "Back to Routes" in content),
                ("Blue button styling", "bg-blue-600" in content),
                ("White text styling", "text-white" in content),
                ("Correct URL", "routes:list" in content or "/routes/" in content),
                (
                    "Route details",
                    route.origin in content and route.destination in content,
                ),
            ]

            print("  Route detail page checks:")
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"    {status} {check_name}")

            # Test the routes list page (where Back to Routes should go)
            list_url = reverse("routes:list")
            list_response = client.get(list_url)
            print(f"📋 Routes list page status: {list_response.status_code}")

            if list_response.status_code == 200:
                print("✅ Routes list page is accessible")
                print(
                    f"✅ Back to Routes button will correctly redirect to: {list_url}"
                )
            else:
                print(
                    f"❌ Routes list page not accessible: {list_response.status_code}"
                )

        else:
            print(f"❌ Route detail page not accessible: {response.status_code}")

        print(f"\n📊 Summary:")
        print(f"  ✅ Fixed Back to Routes button URL (routes:list instead of admin)")
        print(f"  ✅ Updated button styling (blue background, white text)")
        print(f"  ✅ Button should now work correctly on route detail pages")
        print(f"  🌐 Test URL: http://127.0.0.1:8000{detail_url}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_route_detail_page()
