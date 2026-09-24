"""
Add and delete mechanics for `plos_item_list`, shared by any view that renders it.
"""


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
