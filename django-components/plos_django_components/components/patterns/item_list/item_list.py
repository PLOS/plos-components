"""
A component which renders a dynamic, add/delete list of repeating form items.

This module provides:
- A list component with add and delete controls, enhanced with HTMX for partial page updates.
"""

from django_components import register

from ...components.base.base_component import PLOSBaseComponent
from ...components.base.icon_fonts.base_icon import IconFontSetting


@register("plos_item_list")
class ItemList(PLOSBaseComponent):
    """
    A dynamic add/delete item list with HTMX progressive enhancement.

    Renders one accordion section per entry in `values`, headed
    "{Item label} N". Add and delete buttons post the surrounding form to
    `htmx_url`, usually the page's own URL. With HTMX loaded,
    `hx-select` picks the outer `<div id="{name}-item-list">` out of the response
    and swaps it in place. Without HTMX the form submits normally. Either way the
    view applies the action with `logic.apply_action` and re-renders the page.

    Each item is rendered via the `item` slot. Use `data="slot_data"` in the
    fill to access per-item variables:

        slot_data.index: zero-based item index as a str; use for id/name/for attributes
        slot_data.value: the entry from `values` for this item (a str, dict, etc.)
        slot_data.errors: dict of field_id to a list of messages (e.g. slot_data.errors.patent);
                           empty dict when no errors

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

    Collapsed state: with HTMX, `static/plos_django_components/item_list.js` posts
    `{name}__collapsed` (the indexes of collapsed items) on every add and delete. Pass
    `logic.collapsed_after_action(request.POST, name, action)` as `collapsed` so each
    item keeps its state. Items with errors are always expanded, and every item is
    expanded on a full page load.

    Optional display parameters:

        add_label         prefix for the add button label (default: "Add another")
        delete_label      prefix for the delete button label (default: "Delete")
        add_icon_size     plos_icon size for the add icon (default: "xs", 16px)
        delete_icon_size  plos_icon size for the delete icon (default: "md", 24px)
        add_icon          icon class for the add button; defaults to the global add_item icon setting
        delete_icon       icon class for the delete button; defaults to the global delete_item icon setting

    The add and delete controls belong to this pattern, not to plos_button: they are
    styled by the `plos-item-list__add-button` and `plos-item-list__delete-button`
    classes in the item list CSS.

    See the design system page (patterns/item-list) for an interactive demo.
    Its view shows how to read the posted values and apply the add and delete actions.
    """

    template_name = "item_list.html"

    class Media:
        js = ["plos_django_components/item_list.js"]

    def get_context_data(
        self,
        name: str,
        item_label: str,
        values: list,
        max_items: int,
        htmx_url: str,
        item_label_plural: str | None = None,
        errors: list | None = None,
        collapsed: list[int] | None = None,
        add_label: str = "Add another",
        delete_label: str = "Delete",
        add_icon_size: str = "xs",
        delete_icon_size: str = "md",
        add_icon: str | None = None,
        delete_icon: str | None = None,
    ):
        resolved_errors = errors or []
        collapsed_indexes = set(collapsed or [])
        count = len(values)
        items = []
        for i, value in enumerate(values):
            item_errors = {}
            field_errors = resolved_errors[i] if i < len(resolved_errors) else None
            for field_error in field_errors or []:
                item_errors.setdefault(field_error["field_id"], []).append(field_error["message"])
            items.append(
                {
                    "index": str(i),
                    "heading": f"{item_label.capitalize()} {i + 1}",
                    "value": value,
                    "errors": item_errors,
                    "expanded": i not in collapsed_indexes or bool(item_errors),
                }
            )

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
            "remaining": max_items - count,
            "items": items,
            "htmx_url": htmx_url,
            "error_summary": error_summary,
            "add_label": add_label,
            "delete_label": delete_label,
            "add_icon_size": add_icon_size,
            "delete_icon_size": delete_icon_size,
            "add_icon": add_icon if add_icon is not None else IconFontSetting.get_add_item_icon(),
            "delete_icon": delete_icon if delete_icon is not None else IconFontSetting.get_delete_item_icon(),
        }
