from typing import TypedDict

from typing_extensions import NotRequired


class AddMoreField(TypedDict):
    """
    Helper for the field naming mechanisms.
    """

    field_id: NotRequired[str | None]
    field_name: NotRequired[str | None]
    required: NotRequired[bool | None]
    field_value_names: NotRequired[list[str] | None]
