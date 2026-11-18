"""
A list of repeating form items that people can add to and delete from.
"""

from django_components import register

from ...components.base.base_component import PLOSBaseComponent
from ...components.base.icon_fonts.base_icon import IconFontSetting
from .logic import cancelled_index, deleted_index

CONFIRM_DELETE_TEXT = "This action cannot be undone."


def default_confirm_delete_title(item_label: str) -> str:
    """Return the default delete confirmation title."""
    return f"Are you sure you want to delete this {item_label}?"


@register("plos_add_more")
class AddMore(PLOSBaseComponent):
    """
    A dynamic add/delete list of repeating items with HTMX progressive enhancement.

    Renders one accordion section per entry in `values`, headed "{Item label} N". A single
    item is rendered on its own, without the accordion or its heading.
    Each add and delete button posts the surrounding form with `{name}__action` set
    to `add` or `delete__N`. The view reads the posted values, applies the
    action with `logic.apply_add_or_delete` and re-renders the whole page.

    With HTMX loaded, the buttons post to `htmx_url` (usually the page's own URL) and
    `hx-select` swaps only the outer `<div id="{name}-add-more">` from that page.
    Without HTMX the form submits normally and the browser shows the new page.

    Each item is rendered via the `item` slot. Use `data="slot_data"` in the
    fill to access per-item variables:

        slot_data.index: zero-based item index as a str; use for id/name/for attributes
        slot_data.value: the entry from `values` for this item (a str, dict, etc.)
        slot_data.errors: dict of field_id to a list of messages (e.g. slot_data.errors.patent);
                           empty dict when no errors
        slot_data.autofocus: True when this item's first field should take focus; pass it
                              as `autofocus` to that field (see "Focus management" below)

    HTML id convention: field ids in the fill must follow `{field_id}_{slot_data.index}`,
    because `logic.error_summary_entries` links each error to `#{field_id}_{index}`.

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

    Collapsed state: when `last_action` is empty (a page load or a save), only the first
    item is expanded. After an add or delete, with HTMX, `static/plos_django_components/add_more.js`
    posts `{name}__collapsed` (the indexes of collapsed items). Pass
    `logic.collapsed_after_add_or_delete(request.POST, name, action)` as `collapsed` so each
    item keeps its state and new items start expanded. Items with errors are always expanded.
    This relies on the view passing `last_action`.

    Focus management: pass the posted `{name}__action` as `last_action` so focus
    doesn't drop to the page body after an add or delete. The component renders an
    `autofocus` attribute, which browsers honour on a full page load and HTMX honours
    after a swap, so both paths behave the same:

        add          the new item's first field (via `slot_data.autofocus`)
        delete__N    the first field of the item that moved into position N, or the
                     add button when the last item was deleted
        cancel__N    item N's delete link (Cancel on its confirmation, without JS)

    The focused item is always expanded so its field can take focus.

    Optional display parameters:

        remaining_verb    verb in the hint below the add button, as in "You can {verb} 3 more
                          patents" (default: "add")
        max_reached_text  text shown below the add button once max_items is reached, when the
                          button is disabled (default: nothing is shown)
        add_label         prefix for the add button label (default: "Add another")
        delete_label      prefix for the delete button label (default: "Delete")
        add_icon_size     plos_icon size for the add icon (default: "xs", 16px)
        delete_icon_size  plos_icon size for the delete icon (default: "md", 24px)
        add_icon          icon class for the add button; defaults to the global add_item icon setting
        delete_icon       icon class for the delete button; defaults to the global delete_item icon setting

    `error_summary_id` is optional too: the id of the page element wrapping the error
    summary (see "Error summary" above).

    Delete confirmation: by default the delete link asks the user to confirm before
    deleting. Pass `confirm_delete=False` to delete straight away.

        confirm_delete_title  confirmation title (default: "Are you sure you want to delete
                              this {item_label}?")
        confirm_delete_text   confirmation text (default: "This action cannot be undone.")

    With JavaScript, the link opens a `plos_modal` (an `alertdialog`). Without it,
    the confirmation opens inline below the link (see plos_modal), and its
    Cancel button posts `cancel__N`, which reloads the page with the confirmation
    closed. Either way its delete button posts `delete__N`. `apply_add_or_delete`
    leaves the list unchanged for `cancel__N`, so the view needs nothing extra.

    Enter: pressing Enter in a field clicks the form's first submit button. The
    component starts with a hidden submit button named `enter_submits` ("continue" by
    default), so Enter posts that instead of a delete button. Set it to the name of the
    page's main submit button, or None when an earlier submit button already handles
    Enter. The delete confirmations leave theirs out, as this one comes first.

    The add and delete controls belong to this pattern, not to plos_button: they are
    styled by the `plos-add-more__add-button` and `plos-add-more__delete-button`
    classes in the add more CSS.

    The design system page (patterns/add-more) has a demo and a "How to use it" guide
    with the template and view code a page needs.
    """

    template_name = "add_more.html"

    class Media:
        # modal.js too: with confirm_delete, the first modal can arrive in an HTMX swap
        js = ["plos_django_components/add_more.js", "plos_django_components/modal.js"]

    def get_context_data(
        self,
        name: str,
        item_label: str,
        values: list,
        max_items: int,
        htmx_url: str,
        item_label_plural: str | None = None,
        remaining_verb: str = "add",
        max_reached_text: str | None = None,
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
        confirm_delete: bool = True,
        confirm_delete_title: str | None = None,
        confirm_delete_text: str = CONFIRM_DELETE_TEXT,
        enter_submits: str | None = "continue",
    ):
        errors = errors or []
        count = len(values)
        if last_action:
            collapsed_indexes = set(collapsed or [])
        else:
            collapsed_indexes = set(range(1, count))
        focus_index, focus_add_button = self._focus_target(last_action or "", count)
        focus_delete_index = cancelled_index(last_action or "")
        items = []
        for i, value in enumerate(values):
            item_errors = errors[i] if i < len(errors) else None
            messages_by_field = {}
            for field_error in item_errors or []:
                messages_by_field.setdefault(field_error["field_id"], []).append(field_error["message"])
            items.append(
                {
                    "index": str(i),
                    "heading": f"{item_label.capitalize()} {i + 1}",
                    "value": value,
                    "errors": messages_by_field,
                    "autofocus": i == focus_index,
                    "focus_delete": i == focus_delete_index,
                    "expanded": i not in collapsed_indexes or bool(messages_by_field) or i == focus_index,
                }
            )

        return {
            "name": name,
            "item_label": item_label,
            "item_label_plural": item_label_plural or f"{item_label}s",
            "count": count,
            "remaining": max_items - count,
            "remaining_verb": remaining_verb,
            "max_reached_text": max_reached_text,
            "items": items,
            "focus_add_button": focus_add_button,
            "htmx_url": htmx_url,
            "error_summary_oob": f"#{error_summary_id}" if error_summary_id else None,
            "confirm_delete": confirm_delete,
            "confirm_delete_title": confirm_delete_title or default_confirm_delete_title(item_label),
            "confirm_delete_text": confirm_delete_text,
            "enter_submits": enter_submits,
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
        deleted = deleted_index(last_action)
        if deleted is None:
            return None, False
        if deleted < count:
            return deleted, False
        return None, True
