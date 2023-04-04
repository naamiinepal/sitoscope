from django import template

register = template.Library()


@register.filter
def replace(value, arg):
    if len(arg.split("|")) != 2:
        return value

    curr, new = arg.split("|")
    return value.name.replace(curr, new)
