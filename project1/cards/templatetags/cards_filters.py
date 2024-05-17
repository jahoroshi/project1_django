from django import template
from django.utils import timezone
from django.utils.timesince import timesince
from django.utils.timezone import now as django_now

register = template.Library()


@register.filter
def time_left(review_date):
    if review_date is not None:
        now = timezone.now()
        diff = review_date - now
        total_seconds = int(diff.total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        if days > 0:
            return f' In {days} days'
        elif days == 0 and hours > 4:
            return 'Today'
        elif hours <= 4:
            return 'Soon'

    return


@register.filter
def sum_values(dictionary):
    return sum(dictionary.values())
