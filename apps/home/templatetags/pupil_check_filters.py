from django import template

register = template.Library()

@register.filter(name='filter_by_status')
def filter_by_status(queryset, status):
    """Filter pupil checks by status"""
    return queryset.filter(status=status)


