"""
A component function which provides the ability to create a button on any web page.

This module provides:
- A button that can be displayed on any web page.
"""

from typing import Literal

from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_button")
class Button(PLOSBaseComponent):
    """
    A button that can be displayed on any web page.
    """

    template_name = "button_base.html"

    def get_context_data(  # noqa: D102
        self,
        /,
        *,
        disabled: bool = False,
        action: Literal["primary", "secondary", "warning"] = "primary",
        button_type: Literal["button", "reset", "submit"] = "button",
        icon: str | None = None,
        icon_position: Literal["right", "left"] = "right",
        value: str | None = None,
        field_id: str | None = None,
    ):
        return {
            "disabled": disabled,
            "action": action,
            "button_type": button_type,
            "icon": icon,
            "icon_position": icon_position,
            "value": value,
            "field_id": field_id,
        }
