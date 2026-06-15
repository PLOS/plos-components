from typing import TypedDict

from typing_extensions import NotRequired

from ....universal_dictionaries.component_error import PLOSComponentError


class AddMoreValue(TypedDict):
    index: NotRequired[str | None]
    is_first: NotRequired[bool | None]
    errors: NotRequired[list[PLOSComponentError] | None]
    values: NotRequired[dict | None]
