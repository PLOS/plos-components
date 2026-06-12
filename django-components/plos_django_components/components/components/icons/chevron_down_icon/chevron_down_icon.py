"""
Component for rendering a chevron pointing downward icon.
"""

from typing import Literal

from django_components import register

from ...base.base_component import PLOSBaseComponent
from ...base.icon_fonts.base_icon import IconFontSetting


@register("plos_icon_chevron_down")
class ChevronDownIcon(PLOSBaseComponent):
    """
    Renders a chevron pointing downward icon.

    Args:
        size (str, optional): Icon size. One of xs, sm, md, lg, xl.
                              Defaults to md (24px). Passed through to plos_icon_base.
        display (str, optional): Defines the CSS display mode.
                                 Defaults to inline. Passed through to plos_icon_base.

    """

    template_name = "chevron_down_icon.html"

    def get_context_data(  # noqa: D102
        self,
        size: Literal["xs", "sm", "md", "lg", "xl"] = "md",
        display: str = "inline",
        field_id: str | None = None,
    ):
        return {
            "size": size,
            "display": display,
            "field_id": field_id,
            "icon": IconFontSetting.get_chevron_down_icon(),
        }
