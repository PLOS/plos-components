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

@register.filter(name="ds_range")
def ds_range(n):
    return range(n)


@register.filter(name="ds_has_error")
def ds_has_error(item_errors, field_id):
    if not item_errors:
        return False
    return any(e["field_id"] == field_id for e in item_errors)


@register.filter(name="ds_get_error")
def ds_get_error(item_errors, field_id):
    if not item_errors:
        return ""
    for e in item_errors:
        if e["field_id"] == field_id:
            return e["message"]
    return ""
