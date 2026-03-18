from typing import Literal

from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_button")
class TextBox(PLOSBaseComponent):
    template_name = "button_base.html"

    def get_context_data(self,
                         /,
                         *,
                         disabled: bool = False,
                         action: Literal["primary", "secondary", "warning"] = "primary",
                         button_type: Literal["button", "reset", "submit"] = "button",
                         icon: str | None = None,
                         icon_position: Literal["right", "left"] = "right",
    ):
        return {
            "disabled": disabled,
            "action": action,
            "button_type": button_type,
            "icon": icon,
            "icon_position": icon_position,
        }
