#!/usr/bin/env python3
"""
Create comprehensive Freetown bus routes that support both one-way and round-trip bookings.
All routes are scoped to Freetown and surrounding areas only.
"""

import os
import sys
import django
from datetime import time

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from routes.models import Route
from buses.models import Bus, Seat


def create_freetown_routes():
    """Create comprehensive routes within Freetown that support both trip types"""
    print("🚌 Creating Freetown Bus Routes (One-way & Round-trip Support)")
    print("=" * 60)

    # Freetown route definitions with realistic pricing
    freetown_routes = [
        # Central Freetown routes
        {
            "name": "Lumley to Tower Hill Express",
            "origin": "lumley",
            "destination": "tower_hill",
            "price": 15000,  # Le 15,000 (about $0.75)
            "departure_time": time(6, 30),
            "arrival_time": time(7, 15),
            "duration_minutes": 45,
        },
        {
            "name": "Tower Hill to Lumley Return",
            "origin": "tower_hill",
            "destination": "lumley",
            "price": 15000,
            "departure_time": time(7, 30),
            "arrival_time": time(8, 15),
            "duration_minutes": 45,
        },
        # Aberdeen coastal routes
        {
            "name": "Aberdeen to Hill Station",
            "origin": "aberdeen",
            "destination": "hill_station",
            "price": 12000,  # Le 12,000
            "departure_time": time(7, 0),
            "arrival_time": time(7, 30),
            "duration_minutes": 30,
        },
        {
            "name": "Hill Station to Aberdeen",
            "origin": "hill_station",
            "destination": "aberdeen",
            "price": 12000,
            "departure_time": time(8, 0),
            "arrival_time": time(8, 30),
            "duration_minutes": 30,
        },
        # East End routes
        {
            "name": "Kissy to Ferry Junction",
            "origin": "kissy",
            "destination": "ferry_junction",
            "price": 10000,  # Le 10,000
            "departure_time": time(6, 0),
            "arrival_time": time(6, 45),
            "duration_minutes": 45,
        },
        {
            "name": "Ferry Junction to Kissy",
            "origin": "ferry_junction",
            "destination": "kissy",
            "price": 10000,
            "departure_time": time(7, 0),
            "arrival_time": time(7, 45),
            "duration_minutes": 45,
        },
        # Western Area routes
        {
            "name": "Regent Road to Goderich Beach",
            "origin": "regent_road",
            "destination": "goderich",
            "price": 20000,  # Le 20,000 (longer route)
            "departure_time": time(8, 0),
            "arrival_time": time(9, 0),
            "duration_minutes": 60,
        },
        {
            "name": "Goderich to Regent Road",
            "origin": "goderich",
            "destination": "regent_road",
            "price": 20000,
            "departure_time": time(9, 30),
            "arrival_time": time(10, 30),
            "duration_minutes": 60,
        },
        # University routes
        {
            "name": "Wilberforce to Tower Hill Campus",
            "origin": "wilberforce",
            "destination": "tower_hill",
            "price": 8000,  # Le 8,000 (student route)
            "departure_time": time(7, 15),
            "arrival_time": time(7, 45),
            "duration_minutes": 30,
        },
        {
            "name": "Tower Hill to Wilberforce",
            "origin": "tower_hill",
            "destination": "wilberforce",
            "price": 8000,
            "departure_time": time(8, 15),
            "arrival_time": time(8, 45),
            "duration_minutes": 30,
        },
        # Cross-city routes
        {
            "name": "East End to Lumley Cross-City",
            "origin": "east_end",
            "destination": "lumley",
            "price": 25000,  # Le 25,000 (cross-city)
            "departure_time": time(6, 45),
            "arrival_time": time(8, 0),
            "duration_minutes": 75,
        },
        {
            "name": "Lumley to East End Express",
            "origin": "lumley",
            "destination": "east_end",
            "price": 25000,
            "departure_time": time(8, 30),
            "arrival_time": time(9, 45),
            "duration_minutes": 75,
        },
        # Kent Peninsula routes
        {
            "name": "Kent to Aberdeen Coastal",
            "origin": "kent",
            "destination": "aberdeen",
            "price": 18000,  # Le 18,000
            "departure_time": time(9, 0),
            "arrival_time": time(10, 0),
            "duration_minutes": 60,
        },
        {
            "name": "Aberdeen to Kent Peninsula",
            "origin": "aberdeen",
            "destination": "kent",
            "price": 18000,
            "departure_time": time(10, 30),
            "arrival_time": time(11, 30),
            "duration_minutes": 60,
        },
        # Congo Cross routes
        {
            "name": "Congo Cross to Hill Station",
            "origin": "congo_cross",
            "destination": "hill_station",
            "price": 14000,  # Le 14,000
            "departure_time": time(7, 30),
            "arrival_time": time(8, 15),
            "duration_minutes": 45,
        },
        {
            "name": "Hill Station to Congo Cross",
            "origin": "hill_station",
            "destination": "congo_cross",
            "price": 14000,
            "departure_time": time(9, 0),
            "arrival_time": time(9, 45),
            "duration_minutes": 45,
        },
        # Additional peak hour routes
        {
            "name": "Lumley to Kissy Morning Express",
            "origin": "lumley",
            "destination": "kissy",
            "price": 22000,  # Le 22,000
            "departure_time": time(6, 15),
            "arrival_time": time(7, 30),
            "duration_minutes": 75,
        },
        {
            "name": "Kissy to Lumley Evening Express",
            "origin": "kissy",
            "destination": "lumley",
            "price": 22000,
            "departure_time": time(17, 0),
            "arrival_time": time(18, 15),
            "duration_minutes": 75,
        },
        # Weekend special routes
        {
            "name": "Aberdeen Beach Weekend Special",
            "origin": "tower_hill",
            "destination": "aberdeen",
            "price": 16000,  # Le 16,000
            "departure_time": time(10, 0),
            "arrival_time": time(10, 45),
            "duration_minutes": 45,
        },
        {
            "name": "Aberdeen to City Weekend Return",
            "origin": "aberdeen",
            "destination": "tower_hill",
            "price": 16000,
            "departure_time": time(18, 0),
            "arrival_time": time(18, 45),
            "duration_minutes": 45,
        },
    ]

    created_count = 0

    for route_data in freetown_routes:
        # Check if route already exists
        existing_route = Route.objects.filter(
            name=route_data["name"],
            origin=route_data["origin"],
            destination=route_data["destination"],
        ).first()

        if existing_route:
            print(f"⚠️  Route already exists: {route_data['name']}")
            continue

        # Create new route
        try:
            route = Route.objects.create(
                name=route_data["name"],
                origin=route_data["origin"],
                destination=route_data["destination"],
                price=route_data["price"],
                departure_time=route_data["departure_time"],
                arrival_time=route_data["arrival_time"],
                duration_minutes=route_data["duration_minutes"],
                is_active=True,
            )

            print(f"✅ Created: {route.name}")
            print(
                f"   📍 {route.get_origin_display()} → {route.get_destination_display()}"
            )
            print(f"   💰 Price: Le {route.price:,}")
            print(
                f"   🕐 {route.departure_time} → {route.arrival_time} ({route.duration_minutes} mins)"
            )
            print(
                f"   🎫 Supports: One-way (Le {route.price:,}) & Round-trip (Le {route.price * 2:,})"
            )
            print()

            created_count += 1

        except Exception as e:
            print(f"❌ Error creating route {route_data['name']}: {e}")

    print("=" * 60)
    print(f"🎉 Successfully created {created_count} new Freetown routes!")
    print()

    # Display summary
    print("📊 ROUTE SUMMARY:")
    all_routes = Route.objects.all()
    print(f"   Total routes in system: {all_routes.count()}")

    # Group routes by type
    route_types = {}
    for route in all_routes:
        route_key = f"{route.get_origin_display()} ↔ {route.get_destination_display()}"
        if route_key not in route_types:
            route_types[route_key] = []
        route_types[route_key].append(route)

    print(f"   Unique route pairs: {len(route_types)}")
    print()

    print("🔄 ROUND-TRIP CAPABILITY:")
    print("   All routes support both:")
    print("   • One-way bookings (base price)")
    print("   • Round-trip bookings (2x base price)")
    print("   • Automatic price calculation based on trip_type selection")
    print()

    print("🗺️  FREETOWN COVERAGE:")
    locations = set()
    for route in all_routes:
        locations.add(route.get_origin_display())
        locations.add(route.get_destination_display())

    print(f"   Covered locations: {len(locations)}")
    for location in sorted(locations):
        print(f"   • {location}")

    return created_count


def create_sample_buses_for_routes():
    """Create sample buses for the new routes"""
    print("\n🚌 Creating Sample Buses for Routes...")

    routes = Route.objects.all()[:5]  # First 5 routes
    bus_count = 0

    for i, route in enumerate(routes, 1):
        # Check if bus already exists for this route
        if Bus.objects.filter(assigned_route=route).exists():
            continue

        try:
            bus = Bus.objects.create(
                bus_number=f"FL-{i:03d}",
                capacity=30,
                assigned_route=route,
                is_active=True,
            )

            # Create seats for the bus
            for seat_num in range(1, 31):  # 30 seats
                Seat.objects.create(
                    bus=bus, seat_number=f"{seat_num:02d}", is_available=True
                )

            print(f"✅ Created bus {bus.bus_number} for route: {route.name}")
            bus_count += 1

        except Exception as e:
            print(f"❌ Error creating bus for route {route.name}: {e}")

    print(f"🎉 Created {bus_count} buses with seats!")


if __name__ == "__main__":
    print("🚌 WAKA-FINE FREETOWN ROUTES SETUP")
    print("Creating routes that support both one-way and round-trip bookings")
    print("All routes are scoped to Freetown and surrounding areas")
    print()

    created_routes = create_freetown_routes()

    if created_routes > 0:
        create_sample_buses_for_routes()

    print("\n✨ Setup Complete!")
    print("Users can now book:")
    print("• One-way trips at base price")
    print("• Round-trip tickets at 2x base price")
    print("• All routes within Freetown area only")
