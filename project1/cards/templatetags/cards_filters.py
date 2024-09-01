from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def time_left(review_date):
    """
    Calculate and return a human-readable string indicating the time left until a review date.
    :param review_date: The datetime when the review is scheduled
    :return: A string indicating the time left, e.g., 'In X days', 'Today', 'Soon', or 'Ready for Review'
    """
    if review_date is not None:
        now = timezone.now()
        diff = review_date - now
        total_seconds = int(diff.total_seconds())

        # Calculate days, hours
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)

        if days > 0:
            return f'In {days} days'
        elif days == 0 and hours > 4:
            return 'Today'
        elif hours <= 4:
            return 'Soon'

    return 'Ready for Review'


@register.filter
def sum_values(dictionary):
    """
    Return the sum of all values in a dictionary.
    :param dictionary: A dictionary with numerical values
    :return: The sum of the dictionary's values
    """
    return sum(dictionary.values())
