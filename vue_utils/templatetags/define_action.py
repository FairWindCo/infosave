from django import template

register = template.Library()


@register.simple_tag
def define(val=None):
    return val


@register.simple_tag
def create_list(val=None, default_value=None, *args, **kwargs):
    if val is None or val == '':
        val = default_value.split(',')
    elif isinstance(val, str):
        val = val.split(',')
    print(val)
    return val


@register.filter
def create_default_list(val, default_value):
    if val is None or val == '':
        val = default_value.split(',')
    elif isinstance(val, str):
        val = val.split(',')
    print(val)
    return val
