from django import template

register = template.Library()


@register.filter(name="plos_dictionary_fetch")
def plos_dictionary_fetch(dictionary: dict | None, index: str | None):
    if not dictionary:
        return None

    if not index:
        return None

    try:
        return dictionary.get(index)
    except (IndexError, TypeError, ValueError):
        return None
