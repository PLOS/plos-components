"""
A component which renders a dynamic, add/delete list of repeating form items.

This module provides:
- A list component with add and delete controls, enhanced with HTMX for partial page updates.
"""

from ast import literal_eval as ast_literal_eval

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views import View
from django_components import get_component_url, register

from ...components.base.base_component import PLOSBaseComponent
from ...components.base.icon_fonts.base_icon import IconFontSetting
from ...universal_dictionaries.button_dictionary import Button
from ...universal_dictionaries.component_error import PLOSComponentError
from .typed_dict.add_more_fields import AddMoreField
from .typed_dict.add_more_value import AddMoreValue


def get_session_key_values(field_name: str) -> str:
    return f"add_more_{field_name}_values"


def get_session_key_errors(field_name: str) -> str:
    return f"add_more_{field_name}_errors"


def any_field_required(fields: list[AddMoreField] | str) -> bool:
    if isinstance(fields, str):
        try:
            fields = ast_literal_eval(fields)
        except (ValueError, SyntaxError):
            return False

    required = False
    for field in fields:
        if isinstance(field, dict) and field.get("required", False):
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
        fields: list[AddMoreField] | str,
        max_items: int = 10,
        min_items: int = 1,
        count: int | None = None,
        htmx_url: str | None = "/patterns/add-more/htmx/",
        item_label_plural: str | None = None,
        errors: list[PLOSComponentError] | None = None,
        heading_level: int = 2,
        add_label: str = "Add another",
        delete_label: str = "Delete",
        save_label: str = "Save",
        icon_size: str = "xs",
        add_icon: str | None = None,
        delete_icon: str | None = None,
        values: list[AddMoreValue] | str | None = None,
        validation_message: str | None = None,
        show_save_button: bool = False,
        additional_buttons: list[Button] | None = None,
        **kwargs,
    ):
        # State management: if count and values are not provided, try to get them from session
        # This is useful for the initial render and non-HTMX updates.
        request = getattr(self, "request", None) or kwargs.get("request")

        if fields and isinstance(fields, str):
            try:
                fields = ast_literal_eval(fields)
            except (ValueError, SyntaxError):
                fields = []

        if values and isinstance(values, str):
            try:
                values = ast_literal_eval(values)
            except (ValueError, SyntaxError):
                values = None

        session_key_values = get_session_key_values(field_name)
        session_key_errors = get_session_key_errors(field_name)

        if request and hasattr(request, "session"):
            # We want to use values passed from the parent if they exist.
            # However, we also need to respect any changes made during the session
            # (e.g. via HTMX add/delete).
            # If values were passed in, we use them as the base.
            # If session already has values for this field, it means the user has started interacting with it.
            # In that case, we should probably stick with session values to avoid losing user progress.
            # BUT the requirement says: "display the incoming values from the database, but then use the session as
            # is normal"

            session_values = request.session.get(session_key_values, None)

            if values:
                # If values are passed, they override the session values UNLESS we are in an HTMX request
                # or if the user has already interacted with the component in this session?
                # Actually, the patent_example.py clears the session after save.
                # If session_values exist, it means we are in the middle of a session.
                if session_values is None:
                    # First time seeing this component in this session, use passed values.
                    # Convert passed values to the internal format if they aren't already.
                    # Expected internal format: [{"errors": [], "values": {...}}, ...]
                    # patent_example.py passes: [{"patent_number": "...", "patent_description": "..."}, ...]
                    processed_values = []
                    try:
                        for val in values:
                            if isinstance(val, dict):
                                if "values" in val and "errors" in val:
                                    processed_values.append(val)
                                else:
                                    processed_values.append({"errors": [], "values": val})
                            else:
                                raise ValueError("Each value must be a dictionary.")
                        values = processed_values
                    except (ValueError, TypeError, SyntaxError) as e:
                        # Graceful failure with helpful message
                        msg = f"Invalid format for incoming values: {str(e)}"
                        values = [
                            {"errors": [], "values": {}} for _ in range(count if count is not None else min_items)
                        ]
                        if not errors:
                            errors = []
                        errors.append({"field_id": "", "message": msg})

                    request.session[session_key_values] = values
                else:
                    # User is already interacting, use session values.
                    values = session_values
            else:
                # No values passed, use session values.
                values = session_values

            # We pop errors so they don't persist on next refresh
            if not errors:
                errors = request.session.pop(session_key_errors, None)

        if values is None:
            values = [{"errors": [], "values": {}} for _ in range(count if count is not None else min_items)]

        if request and hasattr(request, "session"):
            if request.session.get(session_key_values) is None:
                request.session[session_key_values] = values

        if count is None:
            count = len(values)

        resolved_errors = errors or []
        resolved_values: list[AddMoreValue] = values or []

        add_more_items: list[AddMoreValue] = []
        for i in range(count):
            value: AddMoreValue = resolved_values[i]
            item: AddMoreValue = AddMoreValue()
            item["index"] = str(i)
            item["is_first"] = i == 0
            item["errors"] = value.get("errors", [])
            item["values"] = value.get("values", {})
            add_more_items.append(item)

        show_delete = count > min_items

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
            "error_summary": resolved_errors,
            "has_errors": bool(resolved_errors),
            "heading_level": heading_level,
            "add_label": add_label,
            "delete_label": delete_label,
            "save_label": save_label,
            "icon_size": icon_size,
            "add_icon": add_icon if add_icon is not None else IconFontSetting.get_add_item_icon(),
            "delete_icon": delete_icon if delete_icon is not None else IconFontSetting.get_delete_item_icon(),
            "validation_message": validation_message or f"Enter a {item_label}",
            "show_save_button": show_save_button,
            "additional_buttons": additional_buttons,
        }
        context.update(kwargs)
        return context

    class View(View):
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
                values.append({"errors": [], "values": {}})
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
            # Map values to the format expected by the component
            # If values are already in internal format, keep them
            formatted_values = []
            for v in values:
                if isinstance(v, dict) and "values" in v and "errors" in v:
                    formatted_values.append(v)
                else:
                    formatted_values.append({"errors": [], "values": v})
            request.session[session_key_values] = formatted_values

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
