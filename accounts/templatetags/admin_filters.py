from django import template
from django.db.models import Sum, Avg

register = template.Library()


@register.filter
def sum_field(queryset, field_name):
    """
    Calculate the sum of a specific field in a queryset.
    Usage: {{ tickets|sum_field:"amount_paid" }}
    """
    if not queryset:
        return 0

    if hasattr(queryset, "aggregate"):
        result = queryset.aggregate(total=Sum(field_name))["total"]
        return result if result is not None else 0

    # If it's a list of objects
    total = 0
    for obj in queryset:
        value = getattr(obj, field_name, 0)
        if value:
            total += value
    return total


@register.filter
def avg_field(queryset, field_name):
    """
    Calculate the average of a specific field in a queryset.
    Usage: {{ tickets|avg_field:"amount_paid" }}
    """
    if not queryset:
        return 0

    if hasattr(queryset, "aggregate"):
        result = queryset.aggregate(avg=Avg(field_name))["avg"]
        return result if result is not None else 0

    # If it's a list of objects
    total = 0
    count = 0
    for obj in queryset:
        value = getattr(obj, field_name, 0)
        if value:
            total += value
            count += 1

    return total / count if count > 0 else 0
