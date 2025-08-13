# main/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def add_commas(value):
    """
    Format integer/float with thousand separators. If float, drop decimal if .0
    """
    if value is None:
        return ''
    try:
        # If float has .0, convert to int for nicer formatting
        if isinstance(value, float) and value.is_integer():
            iv = int(value)
            return f"{iv:,}"
        return f"{int(value):,}"
    except (ValueError, TypeError):
        # fallback to string if not numeric
        try:
            s = str(value)
            parts = s.split('.')
            parts[0] = "{:,}".format(int(parts[0]))
            return '.'.join(parts)
        except Exception:
            return s
