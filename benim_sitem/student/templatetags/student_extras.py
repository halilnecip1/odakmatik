# student/templatetags/student_extras.py
from django import template

register = template.Library()

@register.filter
def get_range(value):
    """
    Verilen değere kadar bir sayı aralığı döndürür.
    Örn: 5 | get_range => [1, 2, 3, 4, 5]
    """
    return range(1, value + 1)