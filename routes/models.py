from django.db import models
from django.core.exceptions import ValidationError


class Route(models.Model):
    # Freetown locations
    LOCATION_CHOICES = [
        ("lumley", "Lumley"),
        ("regent_road", "Regent Road"),
        ("aberdeen", "Aberdeen"),
        ("hill_station", "Hill Station"),
        ("kissy", "Kissy"),
        ("east_end", "East End"),
        ("wilberforce", "Wilberforce"),
        ("tower_hill", "Tower Hill"),
        ("ferry_junction", "Ferry Junction"),
        ("goderich", "Goderich"),
        ("kent", "Kent"),
        ("congo_cross", "Congo Cross"),
    ]

    name = models.CharField(max_length=100)
    origin = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    destination = models.CharField(max_length=50, choices=LOCATION_CHOICES)

    # Terminal relationships
    origin_terminal = models.ForeignKey(
        "terminals.Terminal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="origin_routes",
        help_text="Terminal where this route starts",
    )
    destination_terminal = models.ForeignKey(
        "terminals.Terminal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="destination_routes",
        help_text="Terminal where this route ends",
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(help_text="Duration in minutes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["origin", "destination", "departure_time"]

    def clean(self):
        if self.origin == self.destination:
            raise ValidationError("Origin and destination cannot be the same.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_origin_display()} → {self.get_destination_display()}"

    @property
    def origin_display(self):
        """Get origin terminal name if available, otherwise location"""
        if self.origin_terminal:
            return self.origin_terminal.name
        return self.get_origin_display()

    @property
    def destination_display(self):
        """Get destination terminal name if available, otherwise location"""
        if self.destination_terminal:
            return self.destination_terminal.name
        return self.get_destination_display()

    @property
    def duration_formatted(self):
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
