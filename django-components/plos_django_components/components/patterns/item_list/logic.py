"""
Add and delete mechanics for `plos_item_list`, shared by any view that renders it.
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


def apply_action(values: list, action: str, max_items: int, empty_item="") -> list:
    """
    Return a new list with the `{name}__action` add or delete applied.

    `add` appends `empty_item` while under `max_items`. `delete__N` removes item N when
    it exists. The list never becomes empty; deleting the last item leaves one blank.
    Any other action returns the values unchanged.
    """
    values = list(values)
    if action == "add" and len(values) < max_items:
        values.append(empty_item)
    elif action.startswith("delete__"):
        try:
            idx = int(action.removeprefix("delete__"))
        except ValueError:
            idx = -1
        if 0 <= idx < len(values):
            values.pop(idx)
    return values or [empty_item]


def collapsed_after_action(post, name: str, action: str) -> list[int]:
    """
    Return the item indexes the browser posted as collapsed, shifted to match `apply_action`.

    The item list script posts `{name}__collapsed` (e.g. "0,2") with each HTMX add or
    delete. Deleting item N drops N and moves later indexes up by one, so each item keeps
    its own state. New items are not in the set, so they start expanded. Without the
    script (full page loads, no JS) nothing is posted and every item is expanded.
    """
    try:
        collapsed = {int(i) for i in post.get(f"{name}__collapsed", "").split(",") if i}
    except ValueError:
        return []
    if action.startswith("delete__"):
        try:
            deleted = int(action.removeprefix("delete__"))
        except ValueError:
            deleted = -1
        if deleted >= 0:
            collapsed = {i - (i > deleted) for i in collapsed if i != deleted}
    return sorted(collapsed)
