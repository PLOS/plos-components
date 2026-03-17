from typing import Literal

from django.utils.safestring import mark_safe
from django_components import Component, register


@register("plos_button")
class TextBox(Component):
    template_name = "button_base.html"

    def get_context_data(self,
                         /,
                         *,
                         text: str | None = "Submit",
                         disabled: bool = False,
                         action: Literal["primary", "secondary", "warning"] = "primary",
                         type: str = "submit",
                         icon: str | None = None,
                         icon_position: Literal["right", "left"] = "right",
    ):
        return {
            "text": text,
            "disabled": disabled,
            "action": action,
            "type": type,
            "icon": icon,
            "icon_position": icon_position,
        }
