#!/usr/bin/env python3
"""
Sierra Leone Currency Redenomination - Complete Update
Updates pricing from thousands to tens throughout the system
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from routes.models import Route
from bookings.models import Booking
from decimal import Decimal


def update_database_pricing():
    """Update all existing database records"""
    print("=== Updating Database Pricing ===")

    # Define new affordable pricing (Le 5-25 range)
    new_pricing = {
        # Short routes (within city areas)
        ("lumley", "tower_hill"): 15,
        ("tower_hill", "lumley"): 15,
        ("aberdeen", "hill_station"): 12,
        ("hill_station", "aberdeen"): 12,
        ("regent_road", "wilberforce"): 10,
        ("wilberforce", "regent_road"): 10,
        # Medium routes (cross-city)
        ("lumley", "kissy"): 20,
        ("kissy", "lumley"): 20,
        ("east_end", "goderich"): 25,
        ("goderich", "east_end"): 25,
        # Student routes (discounted)
        ("hill_station", "kent"): 8,
        ("kent", "hill_station"): 8,
        # Inter-district routes
        ("tower_hill", "ferry_junction"): 18,
        ("ferry_junction", "tower_hill"): 18,
        ("regent_road", "congo_cross"): 14,
        ("congo_cross", "regent_road"): 14,
        ("aberdeen", "east_end"): 22,
        ("east_end", "aberdeen"): 22,
        ("lumley", "hill_station"): 16,
        ("hill_station", "lumley"): 16,
    }

    print("🚌 Updating Routes...")
    routes_updated = 0

    for route in Route.objects.all():
        route_key = (route.origin, route.destination)

        if route_key in new_pricing:
            new_price = new_pricing[route_key]
        else:
            # For any unlisted routes, convert from thousands to affordable tens
            old_price = float(route.price)
            new_price = max(5, min(25, round(old_price / 1000)))

        old_price = route.price
        route.price = Decimal(str(new_price))
        route.save()

        print(
            f"   {route.origin} → {route.destination}: Le {old_price} → Le {new_price}"
        )
        routes_updated += 1

    print(f"✅ Updated {routes_updated} routes")

    print("\n🎫 Updating Bookings...")
    bookings_updated = 0

    for booking in Booking.objects.all():
        # Get the updated route price
        route_price = float(booking.route.price)

        # Calculate new booking amount based on trip type
        if booking.trip_type == "round_trip":
            new_amount = route_price * 2
        else:
            new_amount = route_price

        old_amount = booking.total_amount
        booking.total_amount = Decimal(str(new_amount))
        booking.amount_paid = Decimal(str(new_amount))
        booking.save()

        print(f"   Booking {booking.pnr_code}: Le {old_amount} → Le {new_amount}")
        bookings_updated += 1

    print(f"✅ Updated {bookings_updated} bookings")

    # Summary
    print("\n📊 New Pricing Summary:")
    unique_prices = set()
    for route in Route.objects.all():
        unique_prices.add(float(route.price))

    sorted_prices = sorted(unique_prices)
    print(f"   Price Range: Le {min(sorted_prices):.0f} - Le {max(sorted_prices):.0f}")
    print(f"   Available Fares: {', '.join([f'Le {p:.0f}' for p in sorted_prices])}")

    print(f"\n✅ Currency redenomination completed!")
    print(f"   - All prices now in affordable tens (Le 5-25)")
    print(f"   - No cents used (whole numbers only)")
    print(f"   - Transportation is now affordable for everyone")


if __name__ == "__main__":
    try:
        update_database_pricing()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
