from django.db import models
from django.core.validators import RegexValidator


class Terminal(models.Model):
    """Bus terminals and bus stops"""

    TERMINAL_TYPE_CHOICES = [
        ("main_terminal", "Main Terminal"),
        ("bus_stop", "Bus Stop"),
        ("interchange", "Interchange"),
        ("depot", "Bus Depot"),
    ]

    CITY_CHOICES = [
        ("freetown", "Freetown"),
        ("bo", "Bo"),
        ("kenema", "Kenema"),
        ("makeni", "Makeni"),
        ("koidu", "Koidu"),
    ]  # Basic Information
    name = models.CharField(max_length=100, unique=True)
    terminal_type = models.CharField(max_length=20, choices=TERMINAL_TYPE_CHOICES)

    # Location Details
    location = models.CharField(max_length=100, help_text="Street address or landmark")
    city = models.CharField(max_length=50, choices=CITY_CHOICES, default="freetown")

    # Terminal Details
    description = models.TextField(
        blank=True, help_text="Additional information about the terminal"
    )
    facilities = models.TextField(
        blank=True, help_text="Available facilities (comma-separated)"
    )

    # Operating Information
    operating_hours_start = models.TimeField(help_text="Terminal opening time")
    operating_hours_end = models.TimeField(help_text="Terminal closing time")
    contact_number = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$", message="Enter a valid phone number"
            )
        ],
    )  # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["city", "name"]
        indexes = [
            models.Index(fields=["city", "terminal_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_terminal_type_display()})"

    def full_address(self):
        return f"{self.location}, {self.get_city_display()}"

    @property
    def facilities_list(self):
        if self.facilities:
            return [facility.strip() for facility in self.facilities.split(",")]
        return []

    @property
    def operating_hours(self):
        return f"{self.operating_hours_start.strftime('%H:%M')} - {self.operating_hours_end.strftime('%H:%M')}"
