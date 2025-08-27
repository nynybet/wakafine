from django import forms
from django.forms import ModelForm
from .models import Terminal


class TerminalForm(ModelForm):
    """Form for creating and editing terminals"""

    class Meta:
        model = Terminal
        fields = [
            "name",
            "terminal_type",
            "location",
            "city",
            "description",
            "facilities",
            "operating_hours_start",
            "operating_hours_end",
            "contact_number",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Enter terminal name",
                }
            ),
            "terminal_type": forms.Select(
                attrs={
                    "class": "form-select w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Street address or landmark",
                }
            ),
            "city": forms.Select(
                attrs={
                    "class": "form-select w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-textarea w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "rows": 3,
                    "placeholder": "Additional information about the terminal",
                }
            ),
            "facilities": forms.Textarea(
                attrs={
                    "class": "form-textarea w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "rows": 2,
                    "placeholder": "Available facilities (comma-separated)",
                }
            ),
            "operating_hours_start": forms.TimeInput(
                attrs={
                    "class": "form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "type": "time",
                }
            ),
            "operating_hours_end": forms.TimeInput(
                attrs={
                    "class": "form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "type": "time",
                }
            ),
            "contact_number": forms.TextInput(
                attrs={
                    "class": "form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "+232XXXXXXXX",
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
        operating_hours_start = cleaned_data.get("operating_hours_start")
        operating_hours_end = cleaned_data.get("operating_hours_end")

        # Validate operating hours
        if (
            operating_hours_start
            and operating_hours_end
            and operating_hours_start >= operating_hours_end
        ):
            raise forms.ValidationError("Opening time must be before closing time.")

        return cleaned_data


class TerminalSearchForm(forms.Form):
    """Form for searching terminals"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                "placeholder": "Search terminals by name, location, or city...",
            }
        ),
    )

    terminal_type = forms.ChoiceField(
        choices=[("", "All Types")] + Terminal.TERMINAL_TYPE_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
            }
        ),
    )

    city = forms.ChoiceField(
        choices=[("", "All Cities")] + Terminal.CITY_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
            }
        ),
    )
