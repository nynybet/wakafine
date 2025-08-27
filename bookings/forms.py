from django import forms
from django.utils import timezone
from .models import Booking
from routes.models import Route
from buses.models import Bus, Seat
from sierra_leone_validator import SierraLeoneMobileValidator


class BookingForm(forms.ModelForm):

    trip_type = forms.ChoiceField(
        choices=Booking.TRIP_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "trip-type-radio"}),
        initial="one_way",
        help_text="Select trip type - round trip pricing is calculated automatically",
    )

    return_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200",
                "style": "display: none;",
            }
        ),
        help_text="Required for round trip bookings",
    )

    class Meta:
        model = Booking
        fields = [
            "route",
            "bus",
            "seat",
            "trip_type",
            "travel_date",
            "return_date",
            "return_bus",
            "return_seat",
        ]
        widgets = {
            "travel_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Apply CSS classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in [
                "trip_type",
                "seat",
                "return_seat",
            ]:  # Skip radio buttons and seat fields
                field.widget.attrs["class"] = (
                    "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200"  # Customize specific fields
                )
        self.fields["route"].queryset = Route.objects.filter(is_active=True)
        self.fields["bus"].queryset = Bus.objects.filter(is_active=True)
        self.fields["return_bus"].queryset = Bus.objects.filter(is_active=True)

        # Make seat fields hidden since they're controlled by JavaScript
        self.fields["seat"].widget = forms.HiddenInput()
        self.fields["return_seat"].widget = forms.HiddenInput()

        # Set seat queryset dynamically based on bus selection
        if args and args[0]:  # If form has POST data
            bus_id = args[0].get("bus")
            if bus_id:
                try:
                    bus = Bus.objects.get(id=bus_id)
                    self.fields["seat"].queryset = Seat.objects.filter(
                        bus=bus, is_available=True
                    )
                except (Bus.DoesNotExist, ValueError):
                    self.fields["seat"].queryset = Seat.objects.none()
            else:
                self.fields["seat"].queryset = Seat.objects.none()
        # If bus is provided in GET parameters, filter seats
        elif "initial" in kwargs and "bus" in kwargs["initial"]:
            try:
                bus_id = kwargs["initial"]["bus"]
                bus = Bus.objects.get(id=bus_id)
                self.fields["seat"].queryset = Seat.objects.filter(
                    bus=bus, is_available=True
                )
            except (Bus.DoesNotExist, ValueError):
                self.fields["seat"].queryset = Seat.objects.none()
        else:
            self.fields["seat"].queryset = Seat.objects.none()

        # Set minimum date to today
        self.fields["travel_date"].widget.attrs["min"] = timezone.now().strftime(
            "%Y-%m-%d"
        )
        self.fields["return_date"].widget.attrs["min"] = timezone.now().strftime(
            "%Y-%m-%d"
        )

    def full_clean(self):
        """Override full_clean to update seat queryset before validation"""
        # Update seat queryset based on submitted data before validation
        if hasattr(self, "data") and self.data.get("bus"):
            try:
                bus_id = self.data.get("bus")
                bus = Bus.objects.get(id=bus_id)
                self.fields["seat"].queryset = Seat.objects.filter(
                    bus=bus, is_available=True
                )
            except (Bus.DoesNotExist, ValueError):
                pass

        super().full_clean()

    def clean_seat(self):
        """Custom validation for seat field to handle dynamic queryset"""
        seat = self.cleaned_data.get("seat")
        bus = self.cleaned_data.get("bus")

        if not seat:
            raise forms.ValidationError("Please select a seat.")

        if not bus:
            raise forms.ValidationError("Please select a bus first.")

        # Check if the seat belongs to the selected bus
        if seat.bus != bus:
            raise forms.ValidationError(
                "The selected seat does not belong to the selected bus."
            )

        # Check if the seat is available
        if not seat.is_available:
            raise forms.ValidationError("The selected seat is not available.")

        # Update the seat queryset for this bus to prevent future validation errors
        self.fields["seat"].queryset = Seat.objects.filter(bus=bus, is_available=True)

        return seat

    def clean(self):
        cleaned_data = super().clean()
        route = cleaned_data.get("route")
        bus = cleaned_data.get("bus")
        seat = cleaned_data.get("seat")
        travel_date = cleaned_data.get("travel_date")
        trip_type = cleaned_data.get("trip_type")
        return_date = cleaned_data.get("return_date")
        return_bus = cleaned_data.get("return_bus")
        return_seat = cleaned_data.get("return_seat")

        # Validate route and bus compatibility
        if route and bus and route != bus.assigned_route:
            raise forms.ValidationError(
                "The selected bus is not assigned to the selected route."
            )

        # Validate seat and bus compatibility
        if seat and bus and seat.bus != bus:
            raise forms.ValidationError(
                "The selected seat does not belong to the selected bus."
            )  # Check travel date is not in the past
        if travel_date:
            # Convert travel_date to date object if it's a datetime
            travel_date_obj = (
                travel_date.date() if hasattr(travel_date, "date") else travel_date
            )
            if travel_date_obj < timezone.now().date():
                raise forms.ValidationError(
                    "Travel date cannot be in the past."
                )  # Validate round trip requirements
        if trip_type == "round_trip":
            if not return_date:
                raise forms.ValidationError(
                    "Return date is required for round trip bookings."
                )
            if not return_bus:
                raise forms.ValidationError(
                    "Return bus is required for round trip bookings."
                )
            if not return_seat:
                raise forms.ValidationError(
                    "Return seat is required for round trip bookings."
                )

            # For round trips, return bus should be compatible with a return route
            # We can be more flexible here - just ensure return seat belongs to return bus
            if return_seat and return_bus and return_seat.bus != return_bus:
                raise forms.ValidationError(
                    "Return seat does not belong to the selected return bus."
                )

            # Check return date is after travel date
            if return_date and travel_date:
                # Convert both to date objects for comparison
                travel_date_obj = (
                    travel_date.date() if hasattr(travel_date, "date") else travel_date
                )
                return_date_obj = (
                    return_date.date() if hasattr(return_date, "date") else return_date
                )

                if return_date_obj <= travel_date_obj:
                    raise forms.ValidationError(
                        "Return date must be after the travel date."
                    )

            # Check return seat availability
            if return_seat and not return_seat.is_available:
                raise forms.ValidationError(
                    "The selected return seat is not available."
                )

            if return_date and travel_date:
                # Convert both to date objects for comparison
                travel_date_obj = (
                    travel_date.date() if hasattr(travel_date, "date") else travel_date
                )
                return_date_obj = (
                    return_date.date() if hasattr(return_date, "date") else return_date
                )

                if return_date_obj <= travel_date_obj:
                    raise forms.ValidationError(
                        "Return date must be after travel date."
                    )

            # Check return seat availability for the return date
            if all([return_bus, return_seat, return_date]):
                return_date_obj = (
                    return_date.date() if hasattr(return_date, "date") else return_date
                )

                existing_return_booking = Booking.objects.filter(
                    bus=return_bus,
                    seat=return_seat,
                    travel_date__date=return_date_obj,
                    status__in=["confirmed", "pending"],
                ).exists()

                # Also check if the return seat is booked as a return seat
                existing_return_seat_booking = Booking.objects.filter(
                    return_bus=return_bus,
                    return_seat=return_seat,
                    return_date__date=return_date_obj,
                    status__in=["confirmed", "pending"],
                ).exists()

                if existing_return_booking or existing_return_seat_booking:
                    raise forms.ValidationError(
                        "The selected return seat is already booked for the return date."
                    )  # Check seat availability
        if all([bus, seat, travel_date]):
            # Convert travel_date to date object if it's not already
            travel_date_obj = (
                travel_date.date() if hasattr(travel_date, "date") else travel_date
            )

            existing_booking = Booking.objects.filter(
                bus=bus,
                seat=seat,
                travel_date__date=travel_date_obj,
                status__in=["confirmed", "pending"],
            ).exists()

            if existing_booking:
                raise forms.ValidationError(
                    "This seat is already booked for the selected date."
                )

        return cleaned_data

    def calculate_total_amount(self):
        """Calculate total amount based on trip type and route price"""
        route = self.cleaned_data.get("route")
        trip_type = self.cleaned_data.get("trip_type")

        if not route:
            return 0

        base_price = route.price

        if trip_type == "round_trip":
            return base_price * 2  # Round trip is double the price
        else:
            return base_price


class BookingSearchForm(forms.Form):
    pnr_code = forms.CharField(
        max_length=10,
        widget=forms.TextInput(
            attrs={
                "class": "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200",
                "placeholder": "Enter your PNR code",
            }
        ),
    )
