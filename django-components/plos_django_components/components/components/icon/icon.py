"""
Component for rendering an icon from an icon font.

This component renders icons from icon fonts (like Bootstrap Icons) in a consistent and accessible way.
See README.md for detailed documentation.
"""

from typing import Literal

from django_components import register

from ..base.base_component import PLOSBaseComponent
from ..base.icon_fonts.abstract_icon_font_defaults import PresetIconName
from ..base.icon_fonts.base_icon import IconFontSetting

# T-shirt size tokens mapped to pixel values. Each token corresponds to a fixed pixel
# dimension applied as the width and height of the icon wrapper.
SIZE_MAP = {
    "xs": 16,
    "sm": 20,
    "md": 24,
    "lg": 32,
    "xl": 40,
}

# Display tokens mapped to CSS classes. "inline" (default) allows the icon to sit
# alongside other HTML elements. "block" places the icon on its own line.
DISPLAY_MAP = {
    "inline": "plos-icon--inline",
    "block": "plos-icon--block",
}


@register("plos_icon")
class Icon(PLOSBaseComponent):
    """
    Renders an icon from an icon font.

    Args:
        icon_name (PresetIconName, optional): The name of the icon to fetch from the IconFontDictionary.
        custom_icon (str, optional): The name of the icon from an icon font (e.g., "bi bi-plus-lg").
        size (str, optional): Icon size. One of xs, sm, md, lg, xl.
                              Defaults to md (24px).
        display (str, optional): Defines the CSS display mode. One of inline, block.
                                 Defaults to inline.
        field_id (str, optional): An ID for the icon element.

    Usage:
        {% component "plos_icon" icon_name="check_circle" size="lg" / %}
        {% component "plos_icon" custom_icon="bi bi-heart-fill" display="block" / %}

    Accessibility:
        Icons are rendered with aria-hidden="true" by default, making them decorative.
        For meaningful icons that convey information, provide alternative text in the parent context.

    See README.md for detailed documentation.
    """

    template_name = "icon.html"

    def get_context_data(  # noqa: D102
        self,
        icon_name: PresetIconName | None = None,
        custom_icon: str | None = None,
        size: Literal["xs", "sm", "md", "lg", "xl"] = "md",
        display: Literal["inline", "block"] = "inline",
        field_id: str | None = None,
    ):
        """
        Process the input parameters and return the context data for rendering the icon.

        This method validates the input parameters and prepares the context data that
        will be passed to the template for rendering the icon component.

        Args:
            icon_name (PresetIconName, optional): The name of the preset icon to use.
                Must be one of the predefined icon names.
            custom_icon (str, optional): A custom icon class from any icon font.
                Takes precedence over icon_name if both are provided.
            size (str, optional): The size of the icon. Must be one of "xs", "sm", "md", "lg", "xl".
                Defaults to "md" (24px).
            display (str, optional): The display mode of the icon. Must be either "inline" or "block".
                Defaults to "inline".
            field_id (str, optional): A custom ID for the icon element.

        Returns:
            dict: A dictionary containing the context data for the template:
                - size_px (int): The size of the icon in pixels.
                - display_class (str): The CSS class for the display mode.
                - field_id (str or None): The custom ID for the icon element, if provided.
                - icon_class (str): The CSS class for the icon from the icon font.

        Raises:
            ValueError: If an invalid size or display mode is provided, or if neither
                icon_name nor custom_icon is provided.
        """
        if size not in SIZE_MAP:
            raise ValueError(f"Invalid icon size '{size}': must be one of {', '.join(SIZE_MAP)}")
        if display not in DISPLAY_MAP:
            raise ValueError(f"Invalid icon display '{display}': must be one of {', '.join(DISPLAY_MAP)}")

        if not icon_name and not custom_icon:
            raise ValueError("Either 'icon_name' or 'custom_icon' must be provided.")

        icon_class = custom_icon
        if icon_name:
            icon_class = IconFontSetting.get_icon(icon_name)

        return {
            "size_px": SIZE_MAP[size],
            "display_class": DISPLAY_MAP[display],
            "field_id": field_id,
            "icon_class": icon_class,
        }
