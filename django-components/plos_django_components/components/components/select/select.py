"""
A component which renders a dynamic select dropdown.
"""
from typing import Literal

from django_components import register

from ....utils.govuk_helper import label_class_from_size
from ..base.base_component import PLOSBaseComponent


@register("plos_select")
class Select(PLOSBaseComponent):
    """
    Renders a dynamic dropdown with label, optional hint, and optional errors.

    Each option dict requires "value" and "text" keys; "selected" is optional (default False).

    Parameters:

        label        label text (required)
        name         form field name (required)
        options      list of dicts: {"value": str, "text": str, "selected": bool}
        value        pre-selected option value -- takes precedence over option["selected"]
        label_size   "large", "medium", or "small" (default "small")
        hide_label   hides the label visually while keeping it accessible (default False)
        hint         hint text shown below the label (default None)
        errors       list of dicts with a "message" key (default [])
        field_id     id attribute for the <select>; defaults to "id_{name}"
        disabled     renders the select as disabled (default False)

    Example usage:

        {% component "plos_select" label="Sort by" name="sort"
            options=[{"value": "recent", "text": "Recently published"}]
        %}{% endcomponent %}
    """

    template_name = "select.html"

    def get_context_data(
        self,
        label: str,
        name: str,
        options: list[dict] | None = None,
        value: str | None = None,
        label_size: Literal["large", "medium", "small"] = "small",
        hide_label: bool = False,
        hint: str | None = None,
        errors: list[dict] | None = None,
        field_id: str | None = None,
        disabled: bool = False,
    ):
        return {
            "label": label,
            "label_class": label_class_from_size(label_size),
            "hide_label": hide_label,
            "name": name,
            "options": options or [],
            "value": value,
            "hint": hint,
            "errors": errors or [],
            "id": field_id or f"id_{name}",
            "disabled": disabled,
        }
