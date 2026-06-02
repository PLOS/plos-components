"""
A component which renders a dynamic, add/delete list of repeating form items.

This module provides:
- A list component with add and delete controls, enhanced with HTMX for partial page updates.
"""

from ast import literal_eval as ast_literal_eval

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django_components import get_component_url, register

from ...components.base.base_component import PLOSBaseComponent
from ...components.base.icon_fonts.base_icon import IconFontSetting
from ...universal_dictionaries.button_dictionary import Button
from .typed_dict.add_more_fields import AddMoreField


def get_session_key_values(field_name: str) -> str:
    return f"add_more_{field_name}_values"


def get_session_key_errors(field_name: str) -> str:
    return f"add_more_{field_name}_errors"


def any_field_required(fields: list[AddMoreField]) -> bool:
    required = False
    for field in fields:
        if field.get("required", False):
            required = True
            break
    return required


def is_required_field(field: AddMoreField) -> bool:
    """
    Returns true if the given field is required, false otherwise.
    :param field: The field to check
    :return: True if the field is required, false otherwise
    """
    return field.get("required", False)


@register("plos_add_more")
class AddMore(PLOSBaseComponent):
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

    template_name = "add_more_partial.html"

    def get_context_data(
        self,
        field_name: str,
        item_label: str,
        fields: list[AddMoreField],
        max_items: int = 10,
        min_items: int = 1,
        count: int | None = None,
        htmx_url: str | None = "/patterns/add-more/htmx/",
        item_label_plural: str | None = None,
        errors: list | None = None,
        heading_level: int = 2,
        add_label: str = "Add another",
        delete_label: str = "Delete",
        save_label: str = "Save",
        icon_size: str = "xs",
        add_icon: str | None = None,
        delete_icon: str | None = None,
        values: list[dict] | None = None,
        validation_message: str | None = None,
        show_save_button: bool = False,
        saved_items_label: str | None = None,
        additional_buttons: list[Button] | None = None,
        **kwargs,
    ):
        # State management: if count and values are not provided, try to get them from session
        # This is useful for the initial render and non-HTMX updates.
        request = getattr(self, "request", None) or kwargs.get("request")
        session_key_values = get_session_key_values(field_name)
        session_key_errors = get_session_key_errors(field_name)

        if values is None and request and hasattr(request, "session"):
            values = request.session.get(session_key_values, None)

        if errors is None and request and hasattr(request, "session"):
            # We pop errors so they don't persist on next refresh
            errors = request.session.pop(session_key_errors, None)

        if values is None:
            values = [{}] * min_items
            if request and hasattr(request, "session"):
                request.session[session_key_values] = values

        if count is None:
            count = len(values)

        resolved_errors = errors or []
        resolved_values: list[dict] = values or []

        def _item_errors_dict(i):
            if i >= len(resolved_errors) or not resolved_errors[i]:
                return {}
            return {field_error["field_id"]: field_error["message"] for field_error in resolved_errors[i]}

        def _item_value(i):
            if i < len(resolved_values):
                return resolved_values[i]
            return ""

        add_more_items = [
            {
                "index": str(i),
                "is_first": i == 0,
                "errors": _item_errors_dict(i),
                "value": _item_value(i),
            }
            for i in range(count)
        ]

        show_delete = count > min_items

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

        if htmx_url is None:
            try:
                htmx_url = get_component_url(AddMore)
            except Exception:
                # If we're not using standard component URLs, fallback to empty
                # which will mean it posts to the current page.
                htmx_url = ""

        remaining: int = max_items - count

        context = {
            "field_name": field_name,
            "item_label": item_label,
            "item_label_plural": item_label_plural or f"{item_label}s",
            "fields": fields,
            "count": count,
            "required": any_field_required(fields),
            "max_items": max_items,
            "min_items": min_items,
            "values": resolved_values,
            "non_empty_values": [v for v in resolved_values if v and (not isinstance(v, str) or v.strip())],
            "show_delete": show_delete,
            "remaining": remaining,
            "add_more_items": add_more_items,
            "htmx_url": htmx_url,
            "error_summary": error_summary,
            "has_errors": bool(error_summary),
            "heading_level": heading_level,
            "add_label": add_label,
            "delete_label": delete_label,
            "save_label": save_label,
            "icon_size": icon_size,
            "add_icon": add_icon if add_icon is not None else IconFontSetting.get_add_item_icon(),
            "delete_icon": delete_icon if delete_icon is not None else IconFontSetting.get_delete_item_icon(),
            "validation_message": validation_message or f"Enter a {item_label}",
            "show_save_button": show_save_button,
            "saved_items_label": saved_items_label or f"Saved {item_label_plural or item_label + 's'}",
            "additional_buttons": additional_buttons,
        }
        context.update(kwargs)
        return context

    class View:
        def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
            # Redirect back to the page that contains the component
            referer = request.META.get("HTTP_REFERER")
            if referer:
                return HttpResponseRedirect(referer)
            return HttpResponseRedirect("/")

        def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
            # Handle add/delete/save actions and return the partial
            field_name = None
            for key in request.POST:
                if key.endswith("__action"):
                    field_name = key[: -len("__action")]
                    break

            if not field_name:
                # If we're here, it might be a standard form submission that was boosted.
                # But for AddMore component, we expect an action.
                return HttpResponse("Missing action name", status=400)

            field_name = field_name.lower().strip()

            try:
                fields_str: str | None = request.POST.get(f"{field_name}__fields")
                if not fields_str:
                    return HttpResponse("Missing field definitions", status=400)
                fields: list[AddMoreField] = ast_literal_eval(fields_str)
            except (ValueError, TypeError, KeyError):
                return HttpResponse("Misconfigured fields definition.", status=400)

            action = request.POST.get(f"{field_name}__action", "")

            try:
                count = int(request.POST.get(f"{field_name}__count", 1))
                max_items = int(request.POST.get(f"{field_name}__max", 10))
                min_items = int(request.POST.get(f"{field_name}__min", 1))
            except (ValueError, TypeError):
                count = 1
                max_items = 10
                min_items = 1

            # Get values to preserve them during HTMX swap
            values: list[dict] = []
            for i in range(count):
                val: dict = {}
                for field in fields:
                    field_id = field.get("field_id")
                    field_value_names: list[str] = field.get("field_value_names", None)
                    field_id_index = f"{field_id}_{i}"
                    if not field_value_names:
                        field_value = request.POST.get(field_id_index, "")
                        val[field_id] = field_value
                    else:
                        consolidated_value: dict = {}
                        for field_value_name in field_value_names:
                            merged_field_name = f"{field_id_index}{field_value_name}"
                            field_value = request.POST.get(merged_field_name, "")
                            consolidated_value[field_value_name] = field_value
                        val[field_id] = consolidated_value
                values.append(val)

            errors = None
            if action == "add" and count < max_items:
                count += 1
                values.append({})
            elif action.startswith("delete__"):
                try:
                    idx = int(action.split("__")[1])
                    if count > min_items:
                        count -= 1
                        if idx < len(values):
                            values.pop(idx)
                except (IndexError, ValueError):
                    pass
            # This needs reworked from the ground up but is preserved for now.
            # elif action == "":  # Save action
            #     if required:
            #         errors: list[list] | None = []
            #         for i, v in enumerate(values):
            #             error: list[dict] = []
            #             for field in fields:
            #                 if not is_required_field(field):
            #                     continue
            #                 field_id: str = field.get("field_id", "")
            #                 val: str | dict = v.get(field_id, "")
            #                 if isinstance(val, str):
            #                     if len(val.strip()) <= 0:
            #                         error.append({"field_id": f"{field_id}_{i}", "message": validation_message})
            #                 else:
            #                     for key, value in val.items():
            #                         if not value.strip():
            #                             error.append(
            #                                 {"field_id": f"{field_id}_{i}{key}", "message": validation_message}
            #                             )
            #             if any(error):
            #                 errors.append(error)
            #         if not any(errors):
            #             errors = None

            session_key_values = get_session_key_values(field_name)
            session_key_errors = get_session_key_errors(field_name)

            # Persist state in session
            request.session[session_key_values] = values

            # Store errors in session so they can be shown after redirect
            request.session[session_key_errors] = errors

            # Always redirect back to the page that contains the component.
            # This ensures that slots (which are defined in the page template)
            # are correctly re-rendered.
            referer = request.META.get("HTTP_REFERER")
            if referer:
                # If we're using hx-boost or HTMX redirect, we want to stay on the same page but refreshed.
                return HttpResponseRedirect(referer)
            return HttpResponseRedirect(request.path)


@register("plos_add_more_item")
class AddMoreItem(PLOSBaseComponent):
    """
    A child component for Add More items.
    """

    template_name = "add_more_item.html"

    def get_context_data(
        self,
        index: int | str,
        display_index: int | str,
        fields: list[AddMoreField],
        field_name: str,
        item_label: str,
        heading_level: int,
        delete_label: str,
        show_delete: bool,
        htmx_url: str,
        errors: dict | None = None,
        value: dict | None = None,
    ):
        return {
            "index": index,
            "display_index": display_index,
            "fields": fields,
            "field_name": field_name,
            "item_label": item_label,
            "heading_level": heading_level,
            "delete_label": delete_label,
            "show_delete": show_delete,
            "htmx_url": htmx_url,
            "errors": errors or {},
            "value": value or {},
        }
