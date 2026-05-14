"""
A component which renders a dynamic, add/delete list of repeating form items.

This module provides:
- A list component with add and delete controls, enhanced with HTMX for partial page updates.
"""

from django_components import register

from ..base.base_component import PLOSBaseComponent
from ..base.icon_fonts.base_icon import IconFontSetting


@register("plos_add_more")
class ItemList(PLOSBaseComponent):
    """
    A dynamic add/delete item list with HTMX progressive enhancement.

    Renders a list of repeating form items. Add and delete buttons submit to
    `htmx_url` via HTMX, swapping only the outer `<div id="{name}-item-list">`
    in place. Without HTMX the same buttons submit the surrounding form normally
    and the page view handles everything.

    Each item is rendered via the `item` slot. Use `data="slot_data"` in the
    fill to access per-item variables:

        slot_data.index  — zero-based item index as a str; use for id/name/for attributes
        slot_data.is_first — True for the first item
        slot_data.errors — dict keyed by base field name (e.g. slot_data.errors.patent,
                           slot_data.errors.coi_description); empty dict when no errors

    HTML id convention: field ids in the fill must follow `{field_id}_{slot_data.index}`
    so the error summary anchors resolve correctly (the component appends _{i} to each
    field_id when building anchor hrefs).

    Error format for the `errors` prop:

        errors = [
            # item 0: no errors
            None,
            # item 1: two field errors
            [
                {"field_id": "coi_description", "message": "Enter a description..."},
                {"field_id": "coi_authors",     "message": "Select whether..."},
            ],
        ]

    `field_id` is the base name without the item index. The component builds one
    error summary entry per field error, formatted as "{Item label N}: {message}",
    linking to #{field_id}_{index}. Errors are rendered inside the HTMX swap
    container so they clear automatically on add/delete swaps.

    Optional display parameters:

        heading_level   heading level for each item heading (default: 2)
        add_label       prefix for the add button label (default: "Add another")
        delete_label    prefix for the delete button label (default: "Delete")
        icon_size       size applied to both add and delete icons (default: "xs")
        add_icon        icon class for the add button; defaults to the global add_item icon setting
        delete_icon     icon class for the delete button; defaults to the global delete_item icon setting

    See the design system page (components/add-more) for a full interactive demo
    and implementation guide.
    """

    template_name = "add_more.html"

    def get_context_data(
        self,
        name: str,
        item_label: str,
        count: int,
        max_items: int,
        htmx_url: str,
        item_label_plural: str | None = None,
        errors: list | None = None,
        heading_level: int = 2,
        add_label: str = "Add another",
        delete_label: str = "Delete",
        icon_size: str = "xs",
        add_icon: str | None = None,
        delete_icon: str | None = None,
    ):
        resolved_errors = errors or []

        def _item_errors_dict(i):
            if i >= len(resolved_errors) or not resolved_errors[i]:
                return {}
            return {field_error["field_id"]: field_error["message"] for field_error in resolved_errors[i]}

        items = [
            {
                "index": str(i),
                "is_first": i == 0,
                "errors": _item_errors_dict(i),
            }
            for i in range(count)
        ]
        error_summary = [
            {
                "label": f"{item_label.capitalize()} {i + 1}",
                "message": field_error["message"],
                "anchor": f"{field_error['field_id']}_{i}",
            }
            for i, item_errors in enumerate(resolved_errors)
            if item_errors
            for field_error in item_errors
        ]
        return {
            "name": name,
            "item_label": item_label,
            "item_label_plural": item_label_plural or f"{item_label}s",
            "count": count,
            "max_items": max_items,
            "remaining": max_items - count,
            "items": items,
            "htmx_url": htmx_url,
            "error_summary": error_summary,
            "has_errors": bool(error_summary),
            "heading_level": heading_level,
            "add_label": add_label,
            "delete_label": delete_label,
            "icon_size": icon_size,
            "add_icon": add_icon if add_icon is not None else IconFontSetting.get_add_item_icon(),
            "delete_icon": delete_icon if delete_icon is not None else IconFontSetting.get_delete_item_icon(),
        }
