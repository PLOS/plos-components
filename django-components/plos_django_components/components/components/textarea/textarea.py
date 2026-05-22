"""
A component which provides for a large textarea input.

This module provides:
- A component for a large textarea input.
"""

from typing import Literal

from django_components import register

from ..base.base_component import PLOSBaseComponent
from ....utils.govuk_helper import label_class_from_size


@register("plos_textarea")
class Textarea(PLOSBaseComponent):
    """
    A component which provides for a a large textarea input.
    """

    template_name = "textarea.html"

    def get_context_data(  # noqa: D102
        self,
        field_id: str,
        name: str,
        label: str | None = None,
        label_size: Literal["large", "medium", "small"] = "small",
        hint: str | None = None,
        placeholder: str | None = None,
        required: bool = False,
        value: str | None = None,
        rows: int = 5,
        cols: int | None = None,
        maxlength: int | None = None,
        minlength: int | None = None,
        errors: list[str] | None = None,
    ):
        return {
            "field_id": field_id,
            "name": name,
            "label": label,
            "label_class": label_class_from_size(label_size),
            "label_size": label_size,
            "hint": hint,
            "placeholder": placeholder,
            "required": required,
            "value": value,
            "rows": rows,
            "cols": cols,
            "maxlength": maxlength,
            "minlength": minlength,
            "errors": errors or [],
        }
