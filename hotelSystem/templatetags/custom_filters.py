from django import template

register = template.Library()

@register.filter(name='replace')
def replace(value, args):
    old, new = args.split(',')
    return value.replace(old, new)

@register.filter
def mul(value, arg):
    try:
        return value * arg
    except (ValueError, TypeError):
        return value