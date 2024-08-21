from django import template
from datetime import date, datetime, timezone

register = template.Library()


@register.filter(expects_localtime=True)
def days_since(value, arg=None):
    try:
        tzinfo = getattr(value, "tzinfo", None)
        value = date(value.year, value.month, value.day)
    except AttributeError:
        return value
    except ValueError:
        return value
    today = datetime.now(tzinfo).date()
    delta = today - value

    return delta.days
