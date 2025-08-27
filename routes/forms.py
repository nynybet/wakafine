from django import forms
from django.forms import ModelForm
from .models import Route
from terminals.models import Terminal


class RouteForm(ModelForm):
    """Form for creating and editing routes with terminal selection"""

    origin_terminal = forms.ModelChoiceField(
        queryset=Terminal.objects.filter(
            terminal_type__in=["main_terminal", "bus_stop", "interchange"]
        ),
        empty_label="Select Origin Terminal",
        widget=forms.Select(
            attrs={
                "class": "form-select w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
            }
        ),
        required=False,
        help_text="Choose the terminal where this route starts",
    )

    destination_terminal = forms.ModelChoiceField(
        queryset=Terminal.objects.filter(
            terminal_type__in=["main_terminal", "bus_stop", "interchange"]
        ),
        empty_label="Select Destination Terminal",
        widget=forms.Select(
            attrs={
                "class": "form-select w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
            }
        ),
        required=False,
        help_text="Choose the terminal where this route ends",
    )

    class Meta:
        model = Route
        fields = [
            "name",
            "origin",
            "destination",
            "origin_terminal",
            "destination_terminal",
            "price",
            "departure_time",
            "arrival_time",
            "duration_minutes",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Enter route name",
                }
            ),
            "origin": forms.Select(
                attrs={
                    "class": "form-select w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                }
            ),
            "destination": forms.Select(
                attrs={
                    "class": "form-select w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),
            "departure_time": forms.TimeInput(
                attrs={
                    "class": "form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "type": "time",
                }
            ),
            "arrival_time": forms.TimeInput(
                attrs={
                    "class": "form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "type": "time",
                }
            ),
            "duration_minutes": forms.NumberInput(
                attrs={
                    "class": "form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "min": "1",
                    "placeholder": "Duration in minutes",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-checkbox h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        origin = cleaned_data.get("origin")
        destination = cleaned_data.get("destination")
        departure_time = cleaned_data.get("departure_time")
        arrival_time = cleaned_data.get("arrival_time")
        duration_minutes = cleaned_data.get("duration_minutes")

        # Validate origin and destination are different
        if origin and destination and origin == destination:
            raise forms.ValidationError("Origin and destination cannot be the same.")

        # Validate time fields
        if departure_time and arrival_time and departure_time >= arrival_time:
            raise forms.ValidationError("Departure time must be before arrival time.")

        # Validate duration is reasonable
        if duration_minutes and duration_minutes < 5:
            raise forms.ValidationError("Duration must be at least 5 minutes.")

        return cleaned_data


class RouteSearchForm(forms.Form):
    """Form for searching routes"""

    origin = forms.ChoiceField(
        choices=[("", "Any Origin")] + Route.LOCATION_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
            }
        ),
    )

    destination = forms.ChoiceField(
        choices=[("", "Any Destination")] + Route.LOCATION_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
            }
        ),
    )

    travel_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                "type": "date",
            }
        ),
    )
