"""
A functional class for processing and providing information about icons.
"""

from django.conf import settings
from django.utils.safestring import SafeString, mark_safe

from .abstract_icon_font_defaults import IconFontDefaultSettings, IconFontDictionary, PresetIconName
from .bootstrap_defaults import bootstrap


class IconFontSetting:
    """
    A settings object for icon fonts.
    """

    _instance = None

    _icon_font: str | None = getattr(settings, "ICON_FONT", "bootstrap")
    _dictionary: IconFontDefaultSettings = None

    def __new__(cls, *args, **kwargs):
        """
        Singleton class ensures only a new item is created if none exists.

        :param args: Args to use.
        :param kwargs: Other optional args.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Constructor.
        """
        if not hasattr(self, "_initialized"):  # Prevent re-initialization on subsequent calls
            if self._icon_font is None:
                self._icon_font = "bootstrap"

            override_dictionary: IconFontDictionary | None = getattr(settings, "ICON_FONT_OVERRIDE_DICTIONARY", None)

            if self._icon_font == "bootstrap":
                self._dictionary = bootstrap(override_dictionary)

            self._initialized = True

    def fetch_icon_font_stylesheet(self) -> SafeString:
        """
        Fetch the icon font style sheet for this icon font.

        :return: A stylesheet for the icon font.
        """
        icon_font_url: str | None = self._dictionary.fetch_icon("icon_font_url")
        icon_font_integrity: str | None = self._dictionary.fetch_icon("icon_font_integrity")

        return mark_safe(
            f"""
            <link rel="stylesheet"
                href="{icon_font_url}"
                {f'integrity="{icon_font_integrity}"' if icon_font_integrity else ""}
                crossorigin="anonymous"
                referrerpolicy="no-referrer" />"""
        )

    def _fetch_icon(self, icon_name: str) -> str | None:
        """
        Fetch the icon from the icon font.

        :param icon_name: The name of the icon to fetch.
        :return: The icon from the icon font.
        """
        return self._dictionary.fetch_icon(icon_name)

    @staticmethod
    def get_icon(icon_name: PresetIconName) -> str | None:
        """
        Gets the icon class for a given preset icon name.

        :param icon_name: The name of the icon to fetch.
        :return: Returns the icon class for the given preset icon name.
        """
        match icon_name:
            case "check_circle":
                return IconFontSetting.get_check_circle_icon()
            case "info_circle":
                return IconFontSetting.get_info_circle_icon()
            case "exclamation_circle":
                return IconFontSetting.get_exclamation_circle_icon()
            case "add_item":
                return IconFontSetting.get_add_item_icon()
            case "delete_item":
                return IconFontSetting.get_delete_item_icon()
            case "chevron_down":
                return IconFontSetting.get_chevron_down_icon()

    @staticmethod
    def get_check_circle_icon() -> str | None:
        """
        Gets the icon class for a check inside a circle icon.

        :return: Returns the icon class for the circle checked icon.
        """
        return IconFontSetting()._fetch_icon("check_circle")

    @staticmethod
    def get_info_circle_icon() -> str | None:
        """
        Gets the icon class for an info inside a circle icon.

        :return: Returns the icon class for the circle information icon.
        """
        return IconFontSetting()._fetch_icon("info_circle")

    @staticmethod
    def get_exclamation_circle_icon() -> str | None:
        """
        Gets the icon class for an exclamation inside a circle icon.

        :return: Returns the icon class for the circle exclamation icon.
        """
        return IconFontSetting()._fetch_icon("exclamation_circle")

    @staticmethod
    def get_add_item_icon() -> str | None:
        """
        Gets the icon class for the add item button.

        :return: Returns the icon class for the add item button.
        """
        return IconFontSetting()._fetch_icon("add_item")

    @staticmethod
    def get_delete_item_icon() -> str | None:
        """
        Gets the icon class for the delete item button.

        :return: Returns the icon class for the delete item button.
        """
        return IconFontSetting()._fetch_icon("delete_item")

    @staticmethod
    def get_chevron_down_icon() -> str | None:
        """
        Gets the icon class for a chevron pointing downward.

        :return: Returns the icon class for the chevron down icon.
        """
        return IconFontSetting()._fetch_icon("chevron_down")
