"""
A component function which provides the ability to create a banner on any web page.

This module provides:
- A banner that can be displayed on any web page.
- Four styles for different types of message banners.
"""

from typing import Literal

from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_banner")
class Banner(PLOSBaseComponent):
    """
    A banner component that displays a specific category of message with accompanying text and an icon
    based on the 'severity' field
    """

    template_name = "banner.html"

    def get_context_data(
        self,
        severity: Literal["success", "warning", "info", "problem"] = "info",
        field_id: str | None = None,
        field_name: str | None = None,
    ):
        return {
            "field_id": field_id,
            "field_name": field_name,
            "severity": severity,
        }
