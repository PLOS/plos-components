"""
A class which defines the icon font types for preset icons as a typed dictionary.
"""

from typing import TypedDict

from typing_extensions import NotRequired


class IconFontDictionary(TypedDict):
    """
    A class which defines the icon font types for preset icons and tracks overrides.
    """

    icon_font_url: NotRequired[str | None]
    icon_font_integrity: NotRequired[str | None]

    check_circle: NotRequired[str | None]

    exclamation_circle: NotRequired[str | None]

    info_circle: NotRequired[str | None]

    add_item: NotRequired[str | None]

    delete_item: NotRequired[str | None]


class IconFontDefaultSettings:
    _icon_font_dictionary: IconFontDictionary
    _icon_font_override_dictionary: IconFontDictionary | None = None

    def __init__(
        self,
        icon_font_dictionary: IconFontDictionary,
        icon_font_override_dictionary: IconFontDictionary | None = None,
    ) -> None:
        """
        Creates a new object for tracking the settings and overrides for given dictionary.
        :param icon_font_dictionary: The font dictionary to pull from with default settings.
        :param icon_font_override_dictionary: The font dictionary to override with optional settings.
        """
        self._icon_font_override_dictionary = icon_font_override_dictionary
        self._icon_font_dictionary = icon_font_dictionary

    def fetch_icon(self, icon_name: str) -> str | None:
        """
        Fetches an icon based on the name.
        :param icon_name: The name of the icon to fetch.
        :return: The icon to be used.
        """
        if self._icon_font_override_dictionary is not None:
            override_icon: str | None = self._icon_font_override_dictionary.get(icon_name, None)
            if override_icon is not None:
                return override_icon

        return self._icon_font_dictionary.get(icon_name, None)
