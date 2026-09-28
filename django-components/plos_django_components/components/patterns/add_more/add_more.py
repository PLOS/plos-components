"""
A component which renders a dynamic, add/delete list of repeating form items.

This module provides:
- A list component with add and delete controls, enhanced with HTMX for partial page updates.
"""

from django_components import register

from ...components.base.base_component import PLOSBaseComponent
from ...components.base.icon_fonts.base_icon import IconFontSetting


@register("plos_add_more")
class AddMore(PLOSBaseComponent):
    """
    A dynamic add/delete list of repeating items with HTMX progressive enhancement.

    Renders one accordion section per entry in `values`, headed
    "{Item label} N". Add and delete buttons post the surrounding form to
    `htmx_url`, usually the page's own URL. With HTMX loaded,
    `hx-select` picks the outer `<div id="{name}-add-more">` out of the response
    and swaps it in place. Without HTMX the form submits normally. Either way the
    view applies the action with `logic.apply_action` and re-renders the page.

    Each item is rendered via the `item` slot. Use `data="slot_data"` in the
    fill to access per-item variables:

        slot_data.index: zero-based item index as a str; use for id/name/for attributes
        slot_data.value: the entry from `values` for this item (a str, dict, etc.)
        slot_data.errors: dict of field_id to a list of messages (e.g. slot_data.errors.patent);
                           empty dict when no errors
        slot_data.autofocus: True when this item's first field should take focus; pass it
                              as `autofocus` to that field (see "Focus management" below)

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

    `field_id` is the base name without the item index. The component shows these
    messages inline on each item; it does not render an error summary.

    Error summary: the page owns it, so a form has one summary for all its fields.
    Build the add more entries with `logic.error_summary_entries(errors, item_label)`
    and add them to the page's own entries. Wrap the page's `plos_error_summary` in an
    element that is always rendered, and pass that element's id as `error_summary_id`:

        <div id="page-errors">
          {% component "plos_error_summary" entries=entries %}{% endcomponent %}
        </div>

    With HTMX, add and delete then also swap that element from the response
    (`hx-select-oob`), so a stale summary doesn't outlive the items it links to.

    Collapsed state: with HTMX, `static/plos_django_components/add_more.js` posts
    `{name}__collapsed` (the indexes of collapsed items) on every add and delete. Pass
    `logic.collapsed_after_action(request.POST, name, action)` as `collapsed` so each
    item keeps its state. Items with errors are always expanded, and every item is
    expanded on a full page load.

    Focus management: pass the posted `{name}__action` as `last_action` so focus
    doesn't drop to the page body after an add or delete. The component renders an
    `autofocus` attribute, which browsers honour on a full page load and HTMX honours
    after a swap, so both paths behave the same:

        add          the new item's first field (via `slot_data.autofocus`)
        delete__N    the first field of the item that moved into position N, or the
                     add button when the last item was deleted

    The focused item is always expanded so its field can take focus.

    Optional display parameters:

        add_label         prefix for the add button label (default: "Add another")
        delete_label      prefix for the delete button label (default: "Delete")
        add_icon_size     plos_icon size for the add icon (default: "xs", 16px)
        delete_icon_size  plos_icon size for the delete icon (default: "md", 24px)
        add_icon          icon class for the add button; defaults to the global add_item icon setting
        delete_icon       icon class for the delete button; defaults to the global delete_item icon setting
        error_summary_id  id of the page element wrapping the error summary; see "Error summary" above

    The add and delete controls belong to this pattern, not to plos_button: they are
    styled by the `plos-add-more__add-button` and `plos-add-more__delete-button`
    classes in the add more CSS.

    See the design system page (patterns/add-more) for an interactive demo.
    Its view shows how to read the posted values and apply the add and delete actions.
    """

    template_name = "add_more.html"

    class Media:
        js = ["plos_django_components/add_more.js"]

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
        last_action: str | None = None,
        add_label: str = "Add another",
        delete_label: str = "Delete",
        add_icon_size: str = "xs",
        delete_icon_size: str = "md",
        add_icon: str | None = None,
        delete_icon: str | None = None,
        error_summary_id: str | None = None,
    ):
        resolved_errors = errors or []
        collapsed_indexes = set(collapsed or [])
        count = len(values)
        focus_index, focus_add_button = self._focus_target(last_action or "", count)
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
                    "autofocus": i == focus_index,
                    "expanded": i not in collapsed_indexes or bool(item_errors) or i == focus_index,
                }
            )

        return {
            "name": name,
            "item_label": item_label,
            "item_label_plural": item_label_plural or f"{item_label}s",
            "count": count,
            "remaining": max_items - count,
            "items": items,
            "focus_add_button": focus_add_button,
            "htmx_url": htmx_url,
            "error_summary_id": error_summary_id,
            "add_label": add_label,
            "delete_label": delete_label,
            "add_icon_size": add_icon_size,
            "delete_icon_size": delete_icon_size,
            "add_icon": add_icon if add_icon is not None else IconFontSetting.get_add_item_icon(),
            "delete_icon": delete_icon if delete_icon is not None else IconFontSetting.get_delete_item_icon(),
        }

    @staticmethod
    def _focus_target(last_action: str, count: int) -> tuple[int | None, bool]:
        """
        Return (item index to focus, whether to focus the add button) after `last_action`.

        `count` is the number of items after the action was applied.
        """
        if last_action == "add":
            return count - 1, False
        if last_action.startswith("delete__"):
            try:
                deleted = int(last_action.removeprefix("delete__"))
            except ValueError:
                return None, False
            if 0 <= deleted < count:
                return deleted, False
            return None, deleted >= 0
        return None, False
