from django import template

register = template.Library()


@register.filter(name="ds_filter_nonempty")
def ds_filter_nonempty(lst):
    try:
        return [v for v in lst if v and v.strip()]
    except (TypeError, AttributeError):
        return []


@register.filter(name="ds_index")
def ds_index(lst, i):
    try:
        return lst[int(i)]
    except (IndexError, TypeError, ValueError):
        return ""
