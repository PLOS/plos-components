from collections import defaultdict
from typing import Literal, TypedDict

from typing_extensions import NotRequired


class _Button(TypedDict, total=False):
    """
    Defines a button into its dictionary representation. Used for patterns which may take multiple buttons as input.
    """

    disabled: NotRequired[bool]
    label: NotRequired[str | None]
    action: NotRequired[Literal["primary", "secondary", "warning"]]
    button_type: NotRequired[Literal["button", "reset", "submit"]]
    icon: NotRequired[str | None]
    icon_position: NotRequired[Literal["right", "left"]]
    value: NotRequired[str | None]
    form_action: NotRequired[str | None]
    field_id: NotRequired[str | None]
    field_name: NotRequired[str | None]
    hx_post: NotRequired[str | None]
    hx_target: NotRequired[str | None]
    hx_swap: NotRequired[str | None]
    hx_include: NotRequired[str | None]
    hx_select: NotRequired[str | None]


class Button(defaultdict):
    """
    A dictionary representation of a button with default values.
    """

    def __init__(self, data: _Button | None = None, **kwargs):
        super().__init__(lambda: None)
        self.update(
            {
                "disabled": False,
                "action": "primary",
                "button_type": "button",
                "icon_position": "right",
            }
        )
        if data:
            self.update({k: v for k, v in data.items() if v is not None})
        self.update({k: v for k, v in kwargs.items() if v is not None})
