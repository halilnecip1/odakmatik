# shop/templatetags/shop_filters.py

from django import template

register = template.Library()

@register.filter
def divide_by_100(value):
    """
    Verilen değeri 100'e böler.
    """
    try:
        return float(value) / 100.0
    except (ValueError, TypeError):
        return value # Hata durumunda orijinal değeri döndür

@register.filter
def currency_format(value):
    """
    Değeri 100'e böler ve para birimi formatında (örn. 12.34) döndürür.
    """
    try:
        tl_value = float(value) / 100.0
        return f"{tl_value:.2f}"
    except (ValueError, TypeError):
        return value # Hata durumunda orijinal değeri döndür