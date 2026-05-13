"""
A component function which provides the ability to create a button group on any web page.

This module provides:
- A button group which can be displayed on any web page.
"""

from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_button_group")
class ButtonGroup(PLOSBaseComponent):
    """
    Component for properly grouping buttons.
    """

    template_name = "button_group.html"

    def get_context_data(self, field_id: str | None = None) -> dict:  # noqa: D102
        return {
            "field_id": field_id,
        }
