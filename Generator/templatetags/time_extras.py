# Generator/templatetags/time_extras.py

from django import template

register = template.Library()

@register.filter
def dictkey(dict_object, key):
    """
    Usage: {{ dict_object|dictkey:key }}
    Returns dict_object[key], or empty list if not found.
    """
    if dict_object is None:
        return []
    return dict_object.get(key, [])


@register.filter
def minutes_to_hhmm(value):
    """
    Convert integer 'value' (representing minutes since midnight)
    into "HH:MM" format.
    """
    try:
        total_minutes = int(value)
        hh = total_minutes // 60
        mm = total_minutes % 60
        return f"{hh:02d}:{mm:02d}"
    except (ValueError, TypeError):
        return value  # Fallback: just return what was given