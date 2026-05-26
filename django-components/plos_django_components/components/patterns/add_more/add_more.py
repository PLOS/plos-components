"""
A component which renders a dynamic, add/delete list of repeating form items.

This module provides:
- A list component with add and delete controls, enhanced with HTMX for partial page updates.
"""

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django_components import get_component_url, register

from ...components.base.base_component import PLOSBaseComponent
from ...components.base.icon_fonts.base_icon import IconFontSetting


@register("plos_add_more")
class AddMore(PLOSBaseComponent):
    """
    A dynamic add/delete add more list with HTMX progressive enhancement.
    """

    template_name = "add_more_partial.html"

    def get_context_data(
        self,
        name: str,
        item_label: str,
        max_items: int = 10,
        min_items: int = 1,
        count: int | None = None,
        htmx_url: str | None = None,
        item_label_plural: str | None = None,
        errors: list | None = None,
        heading_level: int = 2,
        add_label: str = "Add another",
        delete_label: str = "Delete",
        save_label: str = "Save",
        icon_size: str = "xs",
        add_icon: str | None = None,
        delete_icon: str | None = None,
        values: list | None = None,
        required: bool = False,
        validation_message: str | None = None,
        show_save_button: bool = False,
        saved_items_label: str | None = None,
        **kwargs,
    ):
        # State management: if count and values are not provided, try to get them from session
        # This is useful for the initial render and non-HTMX updates.
        request = getattr(self, "request", None) or kwargs.get("request")
        session_key_values = f"add_more_{name}_values"
        session_key_errors = f"add_more_{name}_errors"

        if values is None and request and hasattr(request, "session"):
            values = request.session.get(session_key_values)

        if errors is None and request and hasattr(request, "session"):
            # We pop errors so they don't persist on next refresh
            errors = request.session.pop(session_key_errors, None)

        if values is None:
            values = [""] * min_items
            if request and hasattr(request, "session"):
                request.session[session_key_values] = values

        if count is None:
            count = len(values)

        resolved_errors = errors or []
        resolved_values = values or []

        def _item_errors_dict(i):
            if i >= len(resolved_errors) or not resolved_errors[i]:
                return {}
            return {field_error["field_id"]: field_error["message"] for field_error in resolved_errors[i]}

        def _item_value(i):
            if i < len(resolved_values):
                return resolved_values[i]
            return ""

        items = [
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

        context = {
            "name": name,
            "item_label": item_label,
            "item_label_plural": item_label_plural or f"{item_label}s",
            "count": count,
            "max_items": max_items,
            "min_items": min_items,
            "remaining": max_items - count,
            "items": items,
            "values": resolved_values,
            "non_empty_values": [v for v in resolved_values if v and (not isinstance(v, str) or v.strip())],
            "show_delete": show_delete,
            "remaining": max_items - count,
            "items": items,
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
            "required": required,
            "validation_message": validation_message or f"Enter a {item_label}",
            "show_save_button": show_save_button,
            "saved_items_label": saved_items_label or f"Saved {item_label_plural or item_label + 's'}",
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
            name = None
            for key in request.POST:
                if key.endswith("__action"):
                    name = key[: -len("__action")]
                    break

            if not name:
                # If we're here, it might be a standard form submission that was boosted.
                # But for AddMore component, we expect an action.
                return HttpResponse("Missing action name", status=400)

            action = request.POST.get(f"{name}__action", "")

            try:
                count = int(request.POST.get(f"{name}__count", 1))
                max_items = int(request.POST.get(f"{name}__max", 10))
                min_items = int(request.POST.get(f"{name}__min", 1))
                required = request.POST.get(f"{name}__required") == "True"
                validation_message = request.POST.get(f"{name}__validation_message")
            except (ValueError, TypeError):
                count = 1
                max_items = 10
                min_items = 1
                required = False
                validation_message = None

            # Get values to preserve them during HTMX swap
            item_label = request.POST.get(f"{name}__item_label", "item")
            values = []
            for i in range(count):
                val = request.POST.get(f"{item_label}_{i}", "")
                values.append(val)

            errors = None
            if action == "add" and count < max_items:
                count += 1
                values.append("")
            elif action.startswith("delete__"):
                try:
                    idx = int(action.split("__")[1])
                    if count > min_items:
                        count -= 1
                        if idx < len(values):
                            values.pop(idx)
                except (IndexError, ValueError):
                    pass
            elif action == "":  # Save action
                if required:
                    errors = [
                        [{"field_id": f"{item_label}_{i}", "message": validation_message}] if not v.strip() else None
                        for i, v in enumerate(values)
                    ]
                    if not any(errors):
                        errors = None

            # Persist state in session
            session_key_values = f"add_more_{name}_values"
            request.session[session_key_values] = values

            # Store errors in session so they can be shown after redirect
            if errors:
                session_key_errors = f"add_more_{name}_errors"
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
        name: str,
        item_label: str,
        heading_level: int,
        delete_label: str,
        show_delete: bool,
        htmx_url: str,
        errors: dict | None = None,
    ):
        return {
            "index": index,
            "display_index": display_index,
            "name": name,
            "item_label": item_label,
            "heading_level": heading_level,
            "delete_label": delete_label,
            "show_delete": show_delete,
            "htmx_url": htmx_url,
            "errors": errors or {},
        }
