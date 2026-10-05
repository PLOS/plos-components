"""
A component for rendering a GOV.UK-styled details component.

This module provides:
- A parent component that holds and renders the details content.
"""

from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_details")
class Details(PLOSBaseComponent):
    """
    Defines a details component.

    Args:
        heading (str): The heading displayed in the details button.

    """

    template_name = "details.html"

    def get_context_data(self, heading: str, field_id: str | None = None) -> dict:
        return {
            "field_id": field_id,
            "heading": heading,
        }