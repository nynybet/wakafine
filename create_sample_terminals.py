#!/usr/bin/env python
"""
Script to create sample terminal data for the Waka-Fine Bus system
"""
import os
import sys
import django
from datetime import time

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from terminals.models import Terminal


def create_sample_terminals():
    """Create sample terminals and bus stops"""
    print("🏢 Creating sample terminals and bus stops...")

    terminals_data = [
        {
            "name": "Freetown Central Terminal",
            "terminal_type": "main_terminal",
            "location": "Kissy Street, Central Freetown",
            "city": "freetown",
            "coordinates_lat": "8.4657",
            "coordinates_lng": "-13.2317",
            "description": "Main bus terminal serving all major routes from Freetown",
            "facilities": "Waiting Area, Ticketing Office, Food Court, ATM, Restrooms, Wi-Fi",
            "operating_hours_start": time(5, 0),
            "operating_hours_end": time(22, 0),
            "contact_number": "+23276123456",
            "is_active": True,
        },
        {
            "name": "Aberdeen Bus Stop",
            "terminal_type": "bus_stop",
            "location": "Aberdeen Road, near Lumley Beach",
            "city": "freetown",
            "coordinates_lat": "8.4894",
            "coordinates_lng": "-13.2917",
            "description": "Coastal bus stop serving Aberdeen and beach areas",
            "facilities": "Shelter, Bench Seating",
            "operating_hours_start": time(6, 0),
            "operating_hours_end": time(20, 0),
            "contact_number": "+23276123457",
            "is_active": True,
        },
        {
            "name": "Hill Station Interchange",
            "terminal_type": "interchange",
            "location": "Hill Station Road, Hill Station",
            "city": "freetown",
            "coordinates_lat": "8.4833",
            "coordinates_lng": "-13.2333",
            "description": "Major interchange connecting hill areas to city center",
            "facilities": "Waiting Area, Shelter, Information Board",
            "operating_hours_start": time(5, 30),
            "operating_hours_end": time(21, 30),
            "contact_number": "+23276123458",
            "is_active": True,
        },
        {
            "name": "Lumley Bus Stop",
            "terminal_type": "bus_stop",
            "location": "Lumley Village, near Murray Town",
            "city": "freetown",
            "coordinates_lat": "8.4722",
            "coordinates_lng": "-13.2944",
            "description": "Bus stop serving Lumley residential area",
            "facilities": "Shelter, Basic Seating",
            "operating_hours_start": time(6, 0),
            "operating_hours_end": time(19, 0),
            "contact_number": "+23276123459",
            "is_active": True,
        },
        {
            "name": "Bo Central Terminal",
            "terminal_type": "main_terminal",
            "location": "Bo Town Center, Tiama Road",
            "city": "bo",
            "coordinates_lat": "7.9644",
            "coordinates_lng": "-11.7383",
            "description": "Main terminal in Bo serving southern province routes",
            "facilities": "Waiting Area, Ticketing Office, Food Vendors, Restrooms",
            "operating_hours_start": time(5, 0),
            "operating_hours_end": time(21, 0),
            "contact_number": "+23276123460",
            "is_active": True,
        },
        {
            "name": "Kenema Main Terminal",
            "terminal_type": "main_terminal",
            "location": "Kenema Town Center, Hangha Road",
            "city": "kenema",
            "coordinates_lat": "7.8767",
            "coordinates_lng": "-11.1906",
            "description": "Primary terminal serving eastern province",
            "facilities": "Waiting Area, Ticketing Office, Market Access, Restrooms",
            "operating_hours_start": time(5, 0),
            "operating_hours_end": time(20, 30),
            "contact_number": "+23276123461",
            "is_active": True,
        },
        {
            "name": "Makeni Bus Station",
            "terminal_type": "main_terminal",
            "location": "Makeni City Center, Rogbane Road",
            "city": "makeni",
            "coordinates_lat": "8.8864",
            "coordinates_lng": "-12.0464",
            "description": "Main station serving northern province routes",
            "facilities": "Waiting Area, Ticketing, Food Court, Parking",
            "operating_hours_start": time(5, 0),
            "operating_hours_end": time(21, 0),
            "contact_number": "+23276123462",
            "is_active": True,
        },
        {
            "name": "East End Bus Stop",
            "terminal_type": "bus_stop",
            "location": "East End, near Victoria Park",
            "city": "freetown",
            "coordinates_lat": "8.4667",
            "coordinates_lng": "-13.2306",
            "description": "Bus stop serving East End residential area",
            "facilities": "Basic Shelter, Seating",
            "operating_hours_start": time(6, 0),
            "operating_hours_end": time(19, 30),
            "contact_number": "+23276123463",
            "is_active": True,
        },
        {
            "name": "Kissy Bus Stop",
            "terminal_type": "bus_stop",
            "location": "Kissy Street, Kissy Mess Mess",
            "city": "freetown",
            "coordinates_lat": "8.4611",
            "coordinates_lng": "-13.2278",
            "description": "Bus stop serving Kissy and surrounding areas",
            "facilities": "Shelter, Information Board",
            "operating_hours_start": time(6, 0),
            "operating_hours_end": time(20, 0),
            "contact_number": "+23276123464",
            "is_active": True,
        },
        {
            "name": "Regent Road Bus Stop",
            "terminal_type": "bus_stop",
            "location": "Regent Road, near Regent Village",
            "city": "freetown",
            "coordinates_lat": "8.4389",
            "coordinates_lng": "-13.2028",
            "description": "Bus stop serving Regent Road and mountain areas",
            "facilities": "Shelter, Basic Amenities",
            "operating_hours_start": time(6, 30),
            "operating_hours_end": time(18, 30),
            "contact_number": "+23276123465",
            "is_active": True,
        },
    ]

    created_count = 0
    for terminal_data in terminals_data:
        terminal, created = Terminal.objects.get_or_create(
            name=terminal_data["name"], defaults=terminal_data
        )
        if created:
            created_count += 1
            print(
                f"✅ Created: {terminal.name} ({terminal.get_terminal_type_display()})"
            )
        else:
            print(f"⚠️  Already exists: {terminal.name}")

    print(f"\n📊 Summary:")
    print(f"   • Created {created_count} new terminals")
    print(f"   • Total terminals: {Terminal.objects.count()}")
    print(f"   • Active terminals: {Terminal.objects.filter(is_active=True).count()}")

    # Show breakdown by type
    print(f"\n🏢 Terminal Types:")
    for terminal_type, display_name in Terminal.TERMINAL_TYPE_CHOICES:
        count = Terminal.objects.filter(terminal_type=terminal_type).count()
        print(f"   • {display_name}: {count}")

    # Show breakdown by city
    print(f"\n🌍 By City:")
    for city, display_name in Terminal.CITY_CHOICES:
        count = Terminal.objects.filter(city=city).count()
        print(f"   • {display_name}: {count}")


if __name__ == "__main__":
    create_sample_terminals()
