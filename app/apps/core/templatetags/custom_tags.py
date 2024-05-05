from django import template

register = template.Library()
assignment_tag = register.assignment_tag if hasattr(register, 'assignment_tag') else register.simple_tag


@register.filter(name='times')
def times(number):
    return range(number)


@register.simple_tag
def define(var, val=None):
    return var


@register.filter
def index(indexable, i):
    return indexable[i]
