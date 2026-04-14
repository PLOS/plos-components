from django_components import Component, register

from typing import Literal

@register("banner")
class Banner(Component):
    """
    A banner component that displays a specific category of message with accompanying text and an icon
    based on the 'severity' field
    """

    template_name = "components/banner/banner.html"

    def get_context_data(self, 
                         disabled: bool = False,
                         severity: Literal["success", "warning", "info", "problem"] = "info",
                         field_id: str | None = None,
                         field_name: str | None = None,):    
                return {
                "disabled": disabled,
                "field_id": field_id,
                "field_name": field_name,
                "severity": severity,
            }
