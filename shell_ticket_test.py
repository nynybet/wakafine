from django.test import Client
from django.contrib.auth import get_user_model
from bookings.models import Booking

User = get_user_model()
client = Client()
user = User.objects.get(username="pateh")
client.force_login(user)

booking = Booking.objects.filter(trip_type="round_trip").last()
print(f"Testing booking: {booking.pnr_code}")

response = client.get(f"/bookings/{booking.id}/ticket/")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    content = response.content.decode("utf-8")
    print("Trip Type found:", "Trip Type" in content)
    print("Round Trip found:", "Round Trip" in content)
    print("Return Date found:", "Return Date" in content)
    print("Jul 25, 2025 found:", "Jul 25, 2025" in content)

    # Extract relevant parts
    if "Trip Type" in content:
        start = content.find("Trip Type")
        excerpt = content[start : start + 200]
        print(f"Trip Type section: {excerpt}")

    if "Return Date" in content:
        start = content.find("Return Date")
        excerpt = content[start : start + 200]
        print(f"Return Date section: {excerpt}")
else:
    print("Failed to load page")
