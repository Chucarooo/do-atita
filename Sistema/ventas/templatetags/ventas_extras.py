from django import template

register = template.Library()

@register.filter
def div(value, arg):
    """Divide el valor por el argumento"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def sub(value, arg):
    """Resta el argumento del valor"""
    try:
        return float(value) - float(arg)
    except (ValueError, ZeroDivisionError):
        return 0 