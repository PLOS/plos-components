"""
A class which defines the icon font types for preset icons as a typed dictionary.

This module defines the structure for icon font dictionaries and preset icon names.
It provides type definitions for consistent icon handling across the application.

Key components:
- PresetIconName: Literal type defining available preset icons
- IconFontDictionary: TypedDict for icon font configurations
- IconFontDefaultSettings: Class for managing icon font settings and overrides
"""

from typing import Literal, TypedDict

from typing_extensions import NotRequired

PresetIconName = Literal[
    "check_circle",
    "exclamation_circle",
    "info_circle",
    "add_item",
    "delete_item",
    "chevron_down",
]


class IconFontDictionary(TypedDict):
    """
    A class which defines the icon font types for preset icons and tracks overrides.

    This TypedDict defines the structure for icon font configurations, including:
    - Font loading attributes (icon_font_url, icon_font_integrity)
    - Icon mappings for preset icons (check_circle, exclamation_circle, etc.)

    All fields are NotRequired, allowing for partial configurations.
    """

    icon_font_url: NotRequired[str | None]
    icon_font_integrity: NotRequired[str | None]

    check_circle: NotRequired[str | None]

    exclamation_circle: NotRequired[str | None]

    info_circle: NotRequired[str | None]

    add_item: NotRequired[str | None]

    delete_item: NotRequired[str | None]

    chevron_down: NotRequired[str | None]


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

        Args:
            icon_font_dictionary: The font dictionary to pull from with default settings.
            icon_font_override_dictionary: The font dictionary to override with optional settings.
        """
        self._icon_font_override_dictionary = icon_font_override_dictionary
        self._icon_font_dictionary = icon_font_dictionary

    def fetch_icon(self, icon_name: str) -> str | None:
        """
        Fetches an icon based on the name.

        Args:
            icon_name: The name of the icon to fetch.

        Returns:
            The icon to be used, or None if not found.
        """
        if self._icon_font_override_dictionary is not None:
            override_icon: str | None = self._icon_font_override_dictionary.get(icon_name, None)
            if override_icon is not None:
                return override_icon

        return self._icon_font_dictionary.get(icon_name, None)
