"""
A functional class for processing and providing information about icons.
"""

from django.conf import settings
from django.utils.safestring import SafeString, mark_safe

from .bootstrap_defaults import bootstrap


class IconFontSetting:
    """
    A settings object for icon fonts.
    """

    _instance = None

    _icon_font: str | None = getattr(settings, "ICON_FONT", "bootstrap")
    _icon_font_url: str | None = getattr(settings, "ICON_FONT_URL", None)
    _icon_font_integrity: str | None = getattr(settings, "ICON_FONT_URL", None)
    _dictionary: dict[str, str | None] = None

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

            if self._icon_font == "bootstrap":
                self._dictionary = bootstrap()

            if self._icon_font_url is not None:
                return

            self._icon_font_url = self._dictionary["ICON_FONT_URL"]
            self._icon_font_integrity = self._dictionary["ICON_FONT_INTEGRITY"]

            self._initialized = True

    def fetch_icon_font_stylesheet(self) -> SafeString:
        """
        Fetch the icon font style sheet for this icon font.

        :return: A stylesheet for the icon font.
        """
        return mark_safe(
            f"""
            <link rel="stylesheet"
                href="{self._icon_font_url}"
                {f'integrity="{self._icon_font_integrity}"' if self._icon_font_integrity else ""}
                crossorigin="anonymous"
                referrerpolicy="no-referrer" />"""
        )

    def _fetch_icon(self, icon_override_setting: str, default_const: str) -> str:
        """
        Fetches the string of the class from bootstrap.

        :return: The string of the icon's class from bootstrap.
        """
        icon_override: str | None = getattr(settings, icon_override_setting, None)
        if icon_override is None:
            return self._dictionary[default_const]
        return icon_override

    _check_circle_icon: str | None = None

    @staticmethod
    def get_check_circle_icon() -> str:
        """
        Gets the icon class for a check inside a circle icon.

        :return: Returns the icon class for the circle checked icon.
        """
        if IconFontSetting()._check_circle_icon is None:
            IconFontSetting()._check_circle_icon = IconFontSetting()._fetch_icon(
                "ICON_OVERRIDE_CHECK_CIRCLE", "CHECK_CIRCLE"
            )
        return IconFontSetting()._check_circle_icon

    _info_circle_icon: str | None = None

    @staticmethod
    def get_info_circle_icon() -> str:
        """
        Gets the icon class for a info inside a circle icon.

        :return: Returns the icon class for the circle information icon.
        """
        if IconFontSetting()._info_circle_icon is None:
            IconFontSetting()._info_circle_icon = IconFontSetting()._fetch_icon(
                "ICON_OVERRIDE_INFO_CIRCLE", "INFO_CIRCLE"
            )
        return IconFontSetting()._info_circle_icon

    _exclamation_circle_icon: str | None = None

    @staticmethod
    def get_exclamation_circle_icon() -> str:
        """
        Gets the icon class for a info inside a circle icon.

        :return: Returns the icon class for the circle information icon.
        """
        if IconFontSetting()._exclamation_circle_icon is None:
            IconFontSetting()._exclamation_circle_icon = IconFontSetting()._fetch_icon(
                "ICON_OVERRIDE_EXCLAMATION_CIRCLE", "EXCLAMATION_CIRCLE"
            )
        return IconFontSetting()._exclamation_circle_icon
