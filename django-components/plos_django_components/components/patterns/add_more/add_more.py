"""
A component which renders a dynamic, add/delete list of repeating form items.

This module provides:
- A list component with add and delete controls, enhanced with HTMX for partial page updates.
"""

from ast import literal_eval as ast_literal_eval
from typing import Any, NamedTuple

from django.core import signing
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views import View
from django_components import Empty, get_component_url, register

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


def parse_literal(value: Any, default: Any = None) -> Any:
    """
    Parses a literal string into a Python object using ast.literal_eval.
    """
    if isinstance(value, str):
        try:
            return ast_literal_eval(value)
        except (ValueError, SyntaxError):
            return default
    return value


def any_field_required(fields: list[AddMoreField] | str) -> bool:
    """Check if any field in the list is marked as required."""
    fields_list = parse_literal(fields, [])

    if not isinstance(fields_list, list):
        return False

    return any(field.get("required", False) for field in fields_list if isinstance(field, dict))


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

    class Kwargs(NamedTuple):
        field_name: str
        item_label: str
        fields: list[AddMoreField] | str
        max_items: int = 10
        min_items: int = 1
        count: int | None = None
        htmx_url: str | None = "/patterns/add-more/htmx/"
        item_label_plural: str | None = None
        errors: list[PLOSComponentError] | None = None
        heading_level: int = 2
        add_label: str = "Add another"
        delete_label: str = "Delete"
        save_label: str = "Save"
        icon_size: str = "xs"
        add_icon: str | None = None
        delete_icon: str | None = None
        values: list[AddMoreValue] | str | None = None
        validation_message: str | None = None
        show_save_button: bool = False
        additional_buttons: list[Button] | None = None
        required: bool = False

    Args = Empty

    class Slots(NamedTuple):
        item: Any

    class TemplateData(NamedTuple):
        field_name: str
        item_label: str
        item_label_plural: str
        fields: list[AddMoreField]
        count: int
        required: bool
        max_items: int
        min_items: int
        values: list[AddMoreValue]
        show_delete: bool
        remaining: int
        add_more_items: list[dict]
        htmx_url: str
        error_summary: list[dict]
        has_errors: bool
        heading_level: int
        add_label: str
        delete_label: str
        save_label: str
        icon_size: str
        add_icon: str
        delete_icon: str
        validation_message: str
        show_save_button: bool
        additional_buttons: list[Button]
        last_action: str | None
        last_index: int | None
        autofocus_add_button: bool
        signed_fields: str

    template_name = "add_more_partial.html"

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> TemplateData:
        request = self.request

        fields = parse_literal(kwargs.fields, [])
        values = parse_literal(kwargs.values, None)

        session_key_values = get_session_key_values(kwargs.field_name)
        session_key_errors = get_session_key_errors(kwargs.field_name)

        signed_fields = signing.dumps(fields)

        errors = kwargs.errors

        if request and hasattr(request, "session"):
            session_values = request.session.get(session_key_values)

            if values and session_values is None:
                # First time seeing this component in this session, use passed values.
                values, format_errors = self._format_values(values, kwargs.count, kwargs.min_items)
                request.session[session_key_values] = values
                if format_errors:
                    request.session[session_key_errors] = format_errors
            elif session_values is not None:
                # User is already interacting, use session values.
                values = session_values

            # Pop errors so they don't persist on next refresh
            if not errors:
                errors = request.session.pop(session_key_errors, None)

            # Pop last action/index so they don't persist on next refresh.
            # We use the request object to cache them for the duration of this request
            # in case this component is rendered multiple times.
            cache_key_action = f"_add_more_{kwargs.field_name}_last_action"
            cache_key_index = f"_add_more_{kwargs.field_name}_last_index"
            if hasattr(request, cache_key_action):
                last_action = getattr(request, cache_key_action)
                last_index = getattr(request, cache_key_index)
            else:
                last_action = request.session.pop(f"add_more_{kwargs.field_name}_last_action", None)
                last_index = request.session.pop(f"add_more_{kwargs.field_name}_last_index", None)
                setattr(request, cache_key_action, last_action)
                setattr(request, cache_key_index, last_index)
        else:
            last_action = None
            last_index = None

        if values is None:
            values = [{"errors": [], "values": {}} for _ in range(kwargs.count or kwargs.min_items)]

        if request and hasattr(request, "session") and request.session.get(session_key_values) is None:
            request.session[session_key_values] = values

        count = kwargs.count or len(values)
        resolved_values: list[AddMoreValue] = values
        resolved_errors = self._build_error_summary(errors, kwargs.item_label)

        add_more_items = []
        for i in range(count):
            val = resolved_values[i] if i < len(resolved_values) else {"errors": [], "values": {}}

            # Determine if this item should be autofocused (non-JS)
            item_autofocus_input = False
            item_autofocus_heading = False
            if last_action == "add" and str(last_index) == str(i):
                item_autofocus_input = True
            elif last_action and last_action.startswith("delete__") and str(last_index) == str(i):
                # If we deleted an item, focus the one that took its place
                item_autofocus_heading = True

            add_more_items.append(
                {
                    "index": str(i),
                    "is_first": i == 0,
                    "errors": val.get("errors", []),
                    "values": val.get("values", {}),
                    "autofocus_input": item_autofocus_input,
                    "autofocus_heading": item_autofocus_heading,
                }
            )

        autofocus_add_button = False
        if last_action and last_action.startswith("delete__") and last_index is not None and int(last_index) >= count:
            # If we deleted the last item and it wasn't replaced, focus the add button
            autofocus_add_button = True

        htmx_url = kwargs.htmx_url
        if htmx_url is None:
            try:
                htmx_url = get_component_url(AddMore)
            except Exception:
                htmx_url = ""

        remaining = kwargs.max_items - count

        return AddMore.TemplateData(
            field_name=kwargs.field_name,
            item_label=kwargs.item_label,
            item_label_plural=kwargs.item_label_plural or f"{kwargs.item_label}s",
            fields=fields,
            count=count,
            required=any_field_required(fields),
            max_items=kwargs.max_items,
            min_items=kwargs.min_items,
            values=resolved_values,
            show_delete=count > kwargs.min_items,
            remaining=remaining,
            add_more_items=add_more_items,
            htmx_url=htmx_url,
            error_summary=resolved_errors,
            has_errors=bool(resolved_errors),
            heading_level=kwargs.heading_level,
            add_label=kwargs.add_label,
            delete_label=kwargs.delete_label,
            save_label=kwargs.save_label,
            icon_size=kwargs.icon_size,
            add_icon=kwargs.add_icon or IconFontSetting.get_add_item_icon(),
            delete_icon=kwargs.delete_icon or IconFontSetting.get_delete_item_icon(),
            validation_message=kwargs.validation_message or f"Enter a {kwargs.item_label}",
            show_save_button=kwargs.show_save_button,
            additional_buttons=kwargs.additional_buttons or [],
            last_action=last_action,
            last_index=last_index,
            autofocus_add_button=autofocus_add_button,
            signed_fields=signed_fields,
        )

    def _format_values(self, values: Any, count: int | None, min_items: int) -> tuple[list[dict], list[dict] | None]:
        processed_values = []
        try:
            if not isinstance(values, list):
                raise ValueError("Values must be a list.")
            for val in values:
                if isinstance(val, dict):
                    if "values" in val and "errors" in val:
                        processed_values.append(val)
                    else:
                        processed_values.append({"errors": [], "values": val})
                else:
                    raise ValueError("Each item must be a dictionary.")
            return processed_values, None
        except (ValueError, TypeError):
            return [{"errors": [], "values": {}} for _ in range(count or min_items)], [
                {"message": "Invalid format for incoming values"}
            ]

    def _build_error_summary(self, errors: Any, item_label: str) -> list[dict]:
        """
        Flattens nested errors into a format suitable for plos_error_summary.
        Expected input: [None, [{"field_id": "field", "message": "error"}], ...]
        """
        if not errors or not isinstance(errors, list):
            return errors or []

        flat_errors = []
        for i, item_errors in enumerate(errors):
            if not item_errors:
                continue

            if isinstance(item_errors, list):
                for err in item_errors:
                    if not isinstance(err, dict):
                        continue
                    field_id = err.get("field_id", "")
                    message = err.get("message", "")
                    flat_errors.append(
                        {
                            "label": f"{item_label} {i + 1}",
                            "message": message,
                            "anchor": f"{field_id}_{i}",
                        }
                    )
            elif isinstance(item_errors, dict) and "message" in item_errors:
                flat_errors.append(item_errors)

        return flat_errors

    class View(View):
        def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
            # Redirect back to the page that contains the component
            referer = request.META.get("HTTP_REFERER")
            if referer:
                return HttpResponseRedirect(referer)
            return HttpResponseRedirect("/")

        def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
            field_name = self._get_field_name(request)
            if not field_name:
                return HttpResponse("Missing action name", status=400)

            signed_fields = request.POST.get(f"{field_name}__fields")
            if not signed_fields:
                return HttpResponse("Missing field definitions", status=400)

            try:
                fields = signing.loads(signed_fields)
            except signing.BadSignature:
                return HttpResponse("Invalid or tampered field definitions", status=400)

            action = request.POST.get(f"{field_name}__action", "")
            config = self._get_config(request, field_name)

            values = self._extract_values_from_post(request, field_name, fields, config["count"])

            count = config["count"]
            last_index = None
            if action == "add" and count < config["max_items"]:
                last_index = count  # Index of the new item
                count += 1
                values.append({"errors": [], "values": {}})
            elif action.startswith("delete__"):
                try:
                    last_index = int(action.split("__")[1])
                except (IndexError, ValueError):
                    pass
                values, count = self._handle_delete(action, values, count, config["min_items"])

                # Also handle errors in session when deleting
                session_key_errors = get_session_key_errors(field_name)
                errors = request.session.get(session_key_errors)
                if errors and isinstance(errors, list) and last_index is not None:
                    if last_index < len(errors):
                        errors.pop(last_index)
                        request.session[session_key_errors] = errors

            self._persist_to_session(request, field_name, values, action, last_index)

            referer = request.META.get("HTTP_REFERER")
            if referer:
                return HttpResponseRedirect(referer)
            return HttpResponseRedirect(request.path)

        def _get_field_name(self, request: HttpRequest) -> str | None:
            for key in request.POST:
                if key.endswith("__action"):
                    return key[: -len("__action")].lower().strip()
            return None

        def _get_config(self, request: HttpRequest, field_name: str) -> dict[str, Any]:
            try:
                return {
                    "count": int(request.POST.get(f"{field_name}__count", 1)),
                    "max_items": int(request.POST.get(f"{field_name}__max", 10)),
                    "min_items": int(request.POST.get(f"{field_name}__min", 1)),
                }
            except (ValueError, TypeError):
                return {"count": 1, "max_items": 10, "min_items": 1}

        def _extract_values_from_post(
            self, request: HttpRequest, field_name: str, fields: list[AddMoreField], count: int
        ) -> list[dict]:
            values = []
            for i in range(count):
                item_values = {}
                for field in fields:
                    field_id = field.get("field_id")
                    if not field_id:
                        continue
                    field_value_names = field.get("field_value_names")
                    field_id_index = f"{field_id}_{i}"

                    if not field_value_names:
                        item_values[field_id] = request.POST.get(field_id_index, "")
                    else:
                        item_values[field_id] = {
                            name: request.POST.get(f"{field_id_index}{name}", "") for name in field_value_names
                        }
                values.append({"errors": [], "values": item_values})
            return values

        def _handle_delete(self, action: str, values: list[dict], count: int, min_items: int) -> tuple[list[dict], int]:
            try:
                idx = int(action.split("__")[1])
                if count > min_items and idx < len(values):
                    values.pop(idx)
                    count -= 1
            except (IndexError, ValueError):
                pass
            return values, count

        def _persist_to_session(
            self,
            request: HttpRequest,
            field_name: str,
            values: list[dict],
            last_action: str | None = None,
            last_index: int | None = None,
        ) -> None:
            session_key_values = get_session_key_values(field_name)
            request.session[session_key_values] = values

            if last_action:
                request.session[f"add_more_{field_name}_last_action"] = last_action
            if last_index is not None:
                request.session[f"add_more_{field_name}_last_index"] = last_index


@register("plos_add_more_item")
class AddMoreItem(PLOSBaseComponent):
    """
    A child component for Add More items.
    """

    class Kwargs(NamedTuple):
        index: int | str
        display_index: int | str
        fields: list[AddMoreField]
        field_name: str
        item_label: str
        heading_level: int
        delete_label: str
        show_delete: bool
        htmx_url: str
        is_first: bool = False
        errors: dict | None = None
        value: dict | None = None
        autofocus_heading: bool = False
        autofocus_input: bool = False

    Args = Empty

    class Slots(NamedTuple):
        item_content: Any

    class TemplateData(NamedTuple):
        index: int | str
        display_index: int | str
        fields: list[AddMoreField]
        field_name: str
        item_label: str
        heading_level: int
        delete_label: str
        show_delete: bool
        htmx_url: str
        is_first: bool
        errors: dict
        value: dict
        autofocus_heading: bool
        autofocus_input: bool

    template_name = "add_more_item.html"

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> TemplateData:
        return AddMoreItem.TemplateData(
            index=kwargs.index,
            display_index=kwargs.display_index,
            fields=kwargs.fields,
            field_name=kwargs.field_name,
            item_label=kwargs.item_label,
            heading_level=kwargs.heading_level,
            delete_label=kwargs.delete_label,
            show_delete=kwargs.show_delete,
            htmx_url=kwargs.htmx_url,
            is_first=kwargs.is_first,
            errors=kwargs.errors or {},
            value=kwargs.value or {},
            autofocus_heading=kwargs.autofocus_heading,
            autofocus_input=kwargs.autofocus_input,
        )
