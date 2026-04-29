"""
Public settings for default bootstrap.
"""

from .abstract_icon_font_defaults import IconFontDefaultSettings, IconFontDictionary


def _create_bootstrap_dictionary() -> IconFontDictionary:
    return dict(
        icon_font_url="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.13.1/font/bootstrap-icons.min.css",
        icon_font_integrity="sha512-t7Few9xlddEmgd3oKZQahkNI4dS6l80+eGEzFQiqtyVYdvcSG2D3Iub77R20BdotfRPA9caaRkg1tyaJiPmO0g==",
        check_circle="bi bi-check-circle-fill",
        exclamation_circle="bi bi-exclamation-circle-fill",
        info_circle="bi bi-info-circle-fill",
        add_item="bi bi-plus-lg",
        delete_item="bi bi-trash3",
    )


def bootstrap(override_dictionary: IconFontDictionary | None = None) -> IconFontDefaultSettings:
    """
    Creates a default bootstrap icon font dictionary.

    :param override_dictionary: The dictionary to use for overriding settings, if there is one.
    :return: A default icon font dictionary.
    """
    return IconFontDefaultSettings(_create_bootstrap_dictionary(), override_dictionary)
