from typing import TypedDict

from typing_extensions import NotRequired


class PLOSComponentError(TypedDict):
    """
    Represents an error associated with a form component.
    """

    label: NotRequired[str | None]
    message: NotRequired[str | None]
    anchor: NotRequired[str | None]
