from django import forms
from django.utils import timezone
from django.core.validators import RegexValidator
from .models import Booking
from routes.models import Route
from buses.models import Bus, Seat
import re
from sierra_leone_validator import SierraLeoneMobileValidator


class BookingForm(forms.ModelForm):
    # Sierra Leone phone number validator
    phone_regex = RegexValidator(
        regex=r"^(\+232|232|0)?(7[0-9]|8[0-9]|9[0-9])[0-9]{6}$",
        message="Enter a valid Sierra Leone mobile number (e.g., +232 76 123456 or 076123456)",
    )

    mobile_money_number = forms.CharField(
        max_length=15,
        required=False,
        validators=[phone_regex],
        widget=forms.TextInput(
            attrs={
                "placeholder": "+232 76 123456 or 076123456",
                "class": "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200",
            }
        ),
        help_text="Required for mobile money payments (Afrimoney, Qmoney, Orange Money)",
    )

    class Meta:
        model = Booking
        fields = [
            "route",
            "bus",
            "seat",
            "travel_date",
            "payment_method",
            "mobile_money_number",
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
        super().__init__(*args, **kwargs)

        # Apply CSS classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = (
                "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200"
            )

        # Customize specific fields
        self.fields["route"].queryset = Route.objects.filter(is_active=True)
        self.fields["bus"].queryset = Bus.objects.filter(is_active=True)

        # If bus is provided in GET parameters, filter seats
        if "initial" in kwargs and "bus" in kwargs["initial"]:
            try:
                bus_id = kwargs["initial"]["bus"]
                bus = Bus.objects.get(id=bus_id)
                self.fields["seat"].queryset = Seat.objects.filter(
                    bus=bus, is_available=True
                )
            except (Bus.DoesNotExist, ValueError):
                self.fields["seat"].queryset = Seat.objects.none()
        else:
            self.fields["seat"].queryset = (
                Seat.objects.none()
            )  # Set minimum date to today
        self.fields["travel_date"].widget.attrs["min"] = timezone.now().strftime(
            "%Y-%m-%d"
        )

    def clean(self):
        cleaned_data = super().clean()
        route = cleaned_data.get("route")
        bus = cleaned_data.get("bus")
        seat = cleaned_data.get("seat")
        travel_date = cleaned_data.get("travel_date")

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
        if travel_date and travel_date < timezone.now().date():
            raise forms.ValidationError(
                "Travel date cannot be in the past."
            )  # Check seat availability
        if all([bus, seat, travel_date]):
            existing_booking = Booking.objects.filter(
                bus=bus,
                seat=seat,
                travel_date__date=travel_date,
                status__in=["confirmed", "pending"],
            ).exists()

            if existing_booking:
                raise forms.ValidationError(
                    "This seat is already booked for the selected date."
                )

        # Validate mobile money number for mobile money payments
        payment_method = cleaned_data.get("payment_method")
        mobile_money_number = cleaned_data.get("mobile_money_number")

        mobile_money_methods = ["afrimoney", "qmoney", "orange_money"]

        if payment_method in mobile_money_methods:
            if not mobile_money_number:
                raise forms.ValidationError(
                    f"Mobile money number is required for {payment_method.replace('_', ' ').title()} payments."
                )

            # Use the new validator for validation and normalization
            error_message = SierraLeoneMobileValidator.validate_payment_compatibility(
                payment_method, mobile_money_number
            )
            if error_message:
                raise forms.ValidationError(error_message)
                # Normalize the number
            normalized_number = SierraLeoneMobileValidator.normalize_number(
                mobile_money_number
            )
            if normalized_number:
                cleaned_data["mobile_money_number"] = normalized_number
            else:
                raise forms.ValidationError(
                    "Please enter a valid Sierra Leone mobile number."
                )
        elif payment_method == "paypal":
            # Clear mobile money number for PayPal payments
            cleaned_data["mobile_money_number"] = ""

        return cleaned_data


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
