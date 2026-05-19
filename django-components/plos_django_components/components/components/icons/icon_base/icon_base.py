"""
Base component for rendering SVG icons with consistent sizing.

This component is not intended to be used directly.
Instead, use it as a wrapper around specific icon components that provide the SVG content in the default slot.

Examples:
    Inline (default), suitable for use alongside text:
        {% component "plos_icon_circle_check" size="md" display="inline" %}{% endcomponent %}

    Block, suitable for use as a standalone element:
        {% component "plos_icon_circle_check" size="md" display="block" %}{% endcomponent %}

"""


from django_components import register

from ...base.base_component import PLOSBaseComponent

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


@register("plos_icon_base")
class IconBase(PLOSBaseComponent):
    """
    Renders a sized wrapper around an SVG icon.

    Args:
        size (str, optional): Icon size. One of xs, sm, md, lg, xl.
                              Defaults to md (24px). Invalid values raise an error.
        display (str, optional): CSS display mode. One of inline, block.
                                 Defaults to inline. Invalid values raise an error.

    Use the default slot to provide the SVG content.

    """

    template_name = "icon_base.html"

    def get_context_data(  # noqa: D102
            self,
            size: str = "md",
            display: str = "inline",
            field_id: str | None = None
        ):
        if size not in SIZE_MAP:
            raise ValueError(
                f"Invalid icon size '{size}': must be one of {', '.join(SIZE_MAP)}"
            )
        if display not in DISPLAY_MAP:
            raise ValueError(
                f"Invalid icon display '{display}': must be one of {', '.join(DISPLAY_MAP)}"
            )

        return {
            "size_px": SIZE_MAP[size],
            "display_class": DISPLAY_MAP[display],
            "field_id": field_id
        }
