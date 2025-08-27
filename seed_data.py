#!/usr/bin/env python
import os
import django
import sys
from datetime import time, datetime

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from routes.models import Route
from buses.models import Bus, Seat
from accounts.models import User

# Create sample routes
routes_data = [
    {
        "name": "Lumley to Regent Road Express",
        "origin": "lumley",
        "destination": "regent_road",
        "price": 15000,
        "departure_time": time(8, 0),
        "arrival_time": time(8, 45),
        "duration_minutes": 45,
    },
    {
        "name": "Aberdeen to Hill Station",
        "origin": "aberdeen",
        "destination": "hill_station",
        "price": 12000,
        "departure_time": time(9, 0),
        "arrival_time": time(9, 30),
        "duration_minutes": 30,
    },
    {
        "name": "Kissy to Tower Hill",
        "origin": "kissy",
        "destination": "tower_hill",
        "price": 13500,
        "departure_time": time(10, 0),
        "arrival_time": time(10, 40),
        "duration_minutes": 40,
    },
    {
        "name": "East End to Wilberforce",
        "origin": "east_end",
        "destination": "wilberforce",
        "price": 11000,
        "departure_time": time(11, 0),
        "arrival_time": time(11, 25),
        "duration_minutes": 25,
    },
    {
        "name": "Ferry Junction to Goderich",
        "origin": "ferry_junction",
        "destination": "goderich",
        "price": 14000,
        "departure_time": time(12, 0),
        "arrival_time": time(12, 35),
        "duration_minutes": 35,
    },
    {
        "name": "Kent to Congo Cross",
        "origin": "kent",
        "destination": "congo_cross",
        "price": 10500,
        "departure_time": time(13, 0),
        "arrival_time": time(13, 20),
        "duration_minutes": 20,
    },
]

# Create routes
for route_data in routes_data:
    route, created = Route.objects.get_or_create(**route_data)
    if created:
        print(f"Created route: {route}")

# Create sample buses
buses_data = [
    {
        "bus_number": "WF001",
        "bus_name": "Waka-Fine Express 1",
        "bus_type": "standard",
        "seat_capacity": 25,
    },
    {
        "bus_number": "WF002",
        "bus_name": "Waka-Fine Express 2",
        "bus_type": "mini",
        "seat_capacity": 14,
    },
    {
        "bus_number": "WF003",
        "bus_name": "Waka-Fine Express 3",
        "bus_type": "large",
        "seat_capacity": 35,
    },
    {
        "bus_number": "WF004",
        "bus_name": "Waka-Fine Express 4",
        "bus_type": "standard",
        "seat_capacity": 25,
    },
    {
        "bus_number": "WF005",
        "bus_name": "Waka-Fine Express 5",
        "bus_type": "mini",
        "seat_capacity": 14,
    },
]

# Create buses and assign them to routes
routes = list(Route.objects.all())
for i, bus_data in enumerate(buses_data):
    # Assign route to bus (cycling through available routes)
    if routes:
        bus_data["assigned_route"] = routes[i % len(routes)]

    bus, created = Bus.objects.get_or_create(
        bus_number=bus_data["bus_number"], defaults=bus_data
    )
    if created:
        print(f"Created bus: {bus}")

        # Create seats for the bus
        for seat_num in range(1, bus.seat_capacity + 1):
            seat = Seat.objects.create(
                bus=bus,
                seat_number=f"{seat_num:02d}",
                is_window=(seat_num % 4 in [1, 0]),  # Window seats
            )
        print(f"Created {bus.seat_capacity} seats for {bus}")

# Create sample staff user
staff_user, created = User.objects.get_or_create(
    username="staff",
    defaults={
        "email": "staff@wakafine.sl",
        "first_name": "Staff",
        "last_name": "Member",
        "role": "staff",
        "is_staff": True,
    },
)
if created:
    staff_user.set_password("staff123")
    staff_user.save()
    print("Created staff user")

# Create sample customer
customer, created = User.objects.get_or_create(
    username="customer",
    defaults={
        "email": "customer@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "customer",
        "phone_number": "+232 785 45477",
    },
)
if created:
    customer.set_password("customer123")
    customer.save()
    print("Created customer user")

print("\nSample data created successfully!")
print("\nCredentials:")
print("Admin: admin / admin@1234")
print("Staff: staff / staff123")
print("Customer: customer / customer123")
