"""
Server-side helpers for any view that renders `plos_add_more`: reading the posted
count, applying add and delete, keeping collapsed state, and building error summary
entries.
"""


def posted_count(post, name: str, max_items: int) -> int:
    """
    Return how many items the form posted in `{name}__count`, kept between 1 and `max_items`.

    The count comes from the browser, so it is never trusted: a missing, malformed or
    oversized value can't make the view read more than `max_items` items.
    """
    try:
        count = int(post.get(f"{name}__count", 1))
    except (TypeError, ValueError):
        count = 1
    return max(1, min(count, max_items))


def deleted_index(action: str) -> int | None:
    """
    Return N for a `delete__N` action, or None for any other action.

    None also covers a malformed or negative N, so callers never act on a bad index.
    """
    if not action.startswith("delete__"):
        return None
    try:
        index = int(action.removeprefix("delete__"))
    except ValueError:
        return None
    return index if index >= 0 else None


def apply_add_or_delete(values: list, action: str, max_items: int, empty_item: str | dict = "") -> list:
    """
    Return a new list with the posted `{name}__action` applied.

    `add` appends `empty_item` while under `max_items`. `delete__N` removes item N when
    it exists. The list never becomes empty; deleting the last item leaves one blank.
    Any other action returns the values unchanged.
    """
    values = list(values)
    deleted = deleted_index(action)
    if action == "add" and len(values) < max_items:
        values.append(empty_item)
    elif deleted is not None and deleted < len(values):
        values.pop(deleted)
    return values or [empty_item]


def collapsed_after_add_or_delete(post, name: str, action: str) -> list[int]:
    """
    Return the item indexes the browser posted as collapsed, shifted to match `apply_add_or_delete`.

    The add more script posts `{name}__collapsed` (e.g. "0,2") with each HTMX add or
    delete. Deleting item N drops N and moves later indexes up by one, so each item keeps
    its own state. New items are not in the set, so they start expanded. Without the
    script (full page loads, no JS) nothing is posted and every item is expanded.
    """
    try:
        collapsed = {int(i) for i in post.get(f"{name}__collapsed", "").split(",") if i}
    except ValueError:
        return []
    deleted = deleted_index(action)
    if deleted is not None:
        collapsed = {i - (i > deleted) for i in collapsed if i != deleted}
    return sorted(collapsed)


def error_summary_entries(errors: list | None, item_label: str) -> list[dict]:
    """
    Return `plos_error_summary` entries for the per-item `errors` passed to `plos_add_more`.

    Each field error becomes "{Item label N}: {message}", linking to `{field_id}_{index}`.
    Add these to the page's own entries so the form has a single error summary.
    """
    return [
        {
            "label": f"{item_label.capitalize()} {i + 1}",
            "message": field_error["message"],
            "anchor": f"{field_error['field_id']}_{i}",
        }
        for i, item_errors in enumerate(errors or [])
        if item_errors
        for field_error in item_errors
    ]
