from django import template

register = template.Library()


@register.filter(name="ds_filter_nonempty")
def ds_filter_nonempty(lst):
    try:
        return [v for v in lst if v and v.strip()]
    except (TypeError, AttributeError):
        return []


@register.filter(name="plos_dictionary_fetch")
def plos_dictionary_fetch(dictionary: dict | None, index: str | None):
    if not dictionary:
        return ""

    if not index:
        return ""

    try:
        return dictionary.get(index)
    except (IndexError, TypeError, ValueError):
        return ""


@register.filter(name="plos_list_fetch")
def plos_list_fetch(values: list | tuple | None, index: str | int | None):
    if not values:
        return ""

    if index is None or index == "":
        return ""

    try:
        return values[int(index)]
    except (IndexError, TypeError, ValueError):
        return ""


@register.filter(name="ds_fake_print")
def fake_print(printing: str):
    print(printing)
    return printing
