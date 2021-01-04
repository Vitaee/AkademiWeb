import ast

from django.template.defaulttags import register


@register.filter(name='lookup')
def lookup(d, key):
    return d[key]