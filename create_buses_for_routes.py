#!/usr/bin/env python3
"""
Create buses and seats for the Freetown routes
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from routes.models import Route
from buses.models import Bus, Seat


def create_buses_for_routes():
    """Create buses for routes that don't have buses assigned"""
    print("🚌 Creating Buses for Freetown Routes...")
    print("=" * 50)

    routes_without_buses = Route.objects.filter(bus__isnull=True)

    print(f"Found {routes_without_buses.count()} routes without buses")

    created_buses = 0

    for i, route in enumerate(
        routes_without_buses[:10], 1
    ):  # Create buses for first 10 routes
        try:
            # Create bus
            bus = Bus.objects.create(
                bus_number=f"FT-{i:03d}",  # FT = Freetown
                bus_name=f"Freetown Express {i}",
                bus_type="standard",
                seat_capacity=30,
                assigned_route=route,
                is_active=True,
            )

            # Create 30 seats for the bus
            seats_created = 0
            for seat_num in range(1, 31):
                seat = Seat.objects.create(
                    bus=bus, seat_number=f"{seat_num:02d}", is_available=True
                )
                seats_created += 1

            print(f"✅ Bus {bus.bus_number} created for: {route.name}")
            print(
                f"   📍 Route: {route.get_origin_display()} → {route.get_destination_display()}"
            )
            print(f"   🪑 Seats: {seats_created} created")
            print(
                f"   💰 Route Price: Le {route.price:,} (One-way) / Le {route.price * 2:,} (Round-trip)"
            )
            print()

            created_buses += 1

        except Exception as e:
            print(f"❌ Error creating bus for route {route.name}: {e}")

    print("=" * 50)
    print(f"🎉 Successfully created {created_buses} buses!")

    # Summary
    total_buses = Bus.objects.count()
    total_routes = Route.objects.count()
    routes_with_buses = Route.objects.filter(bus__isnull=False).count()

    print(f"\n📊 SYSTEM SUMMARY:")
    print(f"   Total Routes: {total_routes}")
    print(f"   Total Buses: {total_buses}")
    print(f"   Routes with Buses: {routes_with_buses}")
    print(f"   Routes without Buses: {total_routes - routes_with_buses}")

    return created_buses


if __name__ == "__main__":
    create_buses_for_routes()
