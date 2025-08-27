#!/usr/bin/env python
"""
Script to link existing routes to terminals in the Waka-Fine Bus system
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from routes.models import Route
from terminals.models import Terminal


def link_routes_to_terminals():
    """Link existing routes to appropriate terminals"""
    print("🔗 Linking routes to terminals...")

    # Create mapping of locations to terminals
    location_terminal_map = {
        "lumley": "Lumley Bus Stop",
        "regent_road": "Regent Road Bus Stop",
        "aberdeen": "Aberdeen Bus Stop",
        "hill_station": "Hill Station Interchange",
        "kissy": "Kissy Bus Stop",
        "east_end": "East End Bus Stop",
        # For locations without specific terminals, use main terminal
        "tower_hill": "Freetown Central Terminal",
        "wilberforce": "Freetown Central Terminal",
        "ferry_junction": "Freetown Central Terminal",
        "goderich": "Freetown Central Terminal",
        "kent": "Freetown Central Terminal",
        "congo_cross": "Freetown Central Terminal",
    }

    routes = Route.objects.all()
    updated_count = 0

    for route in routes:
        print(f"\n📍 Processing route: {route}")

        # Find origin terminal
        origin_terminal_name = location_terminal_map.get(route.origin)
        if origin_terminal_name:
            try:
                origin_terminal = Terminal.objects.get(name=origin_terminal_name)
                route.origin_terminal = origin_terminal
                print(f"   ✅ Origin: {origin_terminal.name}")
            except Terminal.DoesNotExist:
                print(f"   ⚠️  Origin terminal '{origin_terminal_name}' not found")

        # Find destination terminal
        dest_terminal_name = location_terminal_map.get(route.destination)
        if dest_terminal_name:
            try:
                dest_terminal = Terminal.objects.get(name=dest_terminal_name)
                route.destination_terminal = dest_terminal
                print(f"   ✅ Destination: {dest_terminal.name}")
            except Terminal.DoesNotExist:
                print(f"   ⚠️  Destination terminal '{dest_terminal_name}' not found")

        # Save the route if terminals were found
        if route.origin_terminal or route.destination_terminal:
            route.save()
            updated_count += 1
            print(f"   💾 Route updated")

    print(f"\n📊 Summary:")
    print(f"   • Updated {updated_count} routes")
    print(f"   • Total routes: {Route.objects.count()}")

    # Show final status
    print(f"\n🔗 Route-Terminal Connections:")
    for route in Route.objects.all():
        origin_term = route.origin_terminal.name if route.origin_terminal else "None"
        dest_term = (
            route.destination_terminal.name if route.destination_terminal else "None"
        )
        print(f"   • {route}: {origin_term} → {dest_term}")


if __name__ == "__main__":
    link_routes_to_terminals()
