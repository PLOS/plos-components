from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .utils.page_title import fetch_design_system_title_from_slug

STYLES = {"column-grid", "colour", "content-design", "spacing", "typography"}

COMPONENTS = {
    "accordion",
    "back-link",
    "button",
    "text-input",
    "textarea",
    "text-box",
    "lists",
    "select",
    "error-summary",
    "file-upload",
    "panel",
    "radios",
    "checkboxes",
    "banner",
    "summary-list",
    "date_input",
    "icon",
    "text-group",
}

PATTERNS = {
    "add-more",
    "check_answers",
    "item-list",
}

ADD_MORE_SUBPAGES = [
    {"slug": "implementation", "label": "Implementation"},
]

ITEM_LIST_SESSION_KEY = "ds_item_list_patents"
ITEM_LIST_MAX = 10

TYPOGRAPHY_SUBPAGES = [
    {"slug": "headings-body", "label": "Headings and Body"},
    {"slug": "functional-text", "label": "Functional Text"},
]


def _nav_context_components(request, active_section=None, active_slug=None, active_subslug=None):
    return _nav_context(request, active_section, active_slug, active_subslug, COMPONENTS)


def _nav_context_patterns(request, active_section=None, active_slug=None, active_subslug=None):
    return _nav_context(request, active_section, active_slug, active_subslug, PATTERNS)


def _nav_context(
    request,
    active_section=None,
    active_slug=None,
    active_subslug=None,
    library: set[str] | None = None,
):
    nav_styles = []
    for s in sorted(STYLES):
        item = {
            "slug": s,
            "label": fetch_design_system_title_from_slug(s),
            "children": [],
        }
        if s == "typography":
            item["children"] = TYPOGRAPHY_SUBPAGES
        nav_styles.append(item)

    nav_components = None
    if library is not None:
        nav_components = []
        for c in sorted(library):
            item = {
                "slug": c,
                "label": fetch_design_system_title_from_slug(c),
                "children": [],
            }
            if c == "add-more":
                item["children"] = ADD_MORE_SUBPAGES
            nav_components.append(item)

    return {
        "nav_styles": nav_styles,
        "nav_components": nav_components,
        "active_section": active_section,
        "active_slug": active_slug,
        "active_subslug": active_subslug,
        "current_path": request.path,
    }


def _build_page_context(request):
    return _nav_context_patterns(request, active_section="patterns", active_slug="add-more")


def design_system_index(request):
    return render(request, "design_system/index.html", _nav_context(request))


def design_system_styles_index(request):
    ctx = _nav_context(request, active_section="styles")
    ctx["styles"] = ctx["nav_styles"]
    return render(request, "design_system/styles/index.html", ctx)


def design_system_components_index(request):
    ctx = _nav_context_components(request, active_section="components")
    ctx["components"] = ctx["nav_components"]
    return render(request, "design_system/components/index.html", ctx)


def design_system_patterns_index(request):
    ctx = _nav_context_patterns(request, active_section="patterns")
    ctx["components"] = ctx["nav_components"]
    return render(request, "design_system/patterns/index.html", ctx)


def design_system_typography(request, page):
    slug = page.replace("-", "_")
    return render(
        request,
        f"design_system/styles/typography/{slug}.html",
        _nav_context(
            request,
            active_section="styles",
            active_slug="typography",
            active_subslug=page,
        ),
    )


def design_system_style(request, page):
    slug = page.replace("-", "_")
    return render(
        request,
        f"design_system/styles/{slug}.html",
        _nav_context(request, active_section="styles", active_slug=page),
    )


def add_more_htmx_page(request):
    return render(request, "design_system/patterns/add_more.html", _build_page_context(request))


def add_more_implementation_page(request):
    ctx = _nav_context_patterns(
        request,
        active_section="patterns",
        active_slug="add-more",
        active_subslug="implementation",
    )
    return render(request, "design_system/patterns/add_more/implementation.html", ctx)


def _parse_delete_idx(action):
    try:
        return int(action.split("__")[1])
    except (IndexError, ValueError):
        return None


def _item_list_page_context(request, patent_values=None, patent_errors=None):
    if patent_values is None:
        patent_values = request.session.get(ITEM_LIST_SESSION_KEY)
        if patent_values is None:
            patent_values = [""]
            request.session[ITEM_LIST_SESSION_KEY] = patent_values

    ctx = _nav_context_patterns(request, active_section="patterns", active_slug="item-list")
    ctx["count"] = len(patent_values)
    ctx["patent_values"] = patent_values
    ctx["htmx_url"] = reverse("item_list_htmx")
    if patent_errors is not None:
        ctx["errors"] = patent_errors
    return ctx


def item_list_page(request):
    if request.method == "POST" and not request.headers.get("HX-Request"):
        return _item_list_handle_post(request)
    return render(request, "design_system/patterns/item_list.html", _item_list_page_context(request))


def _item_list_handle_post(request):
    """Handle a full-page POST, used when HTMX is not loaded."""
    saved = request.session.get(ITEM_LIST_SESSION_KEY, [""])
    try:
        count = min(int(request.POST.get("patents__count", len(saved))), ITEM_LIST_MAX)
    except (ValueError, TypeError):
        count = len(saved)
    values = [request.POST.get(f"patent_{i}", "") for i in range(count)]
    action = request.POST.get("patents__action", "")
    url = reverse("design_system_pattern", kwargs={"pattern": "item-list"})

    if action == "add" or action.startswith("delete__"):
        anchor = "#patents-list-anchor"
        if action == "add" and count < ITEM_LIST_MAX:
            values.append("")
        elif action.startswith("delete__"):
            idx = _parse_delete_idx(action)
            if idx is not None:
                try:
                    values.pop(idx)
                except IndexError:
                    idx = None
            if not values:
                values = [""]
            if idx is not None and idx < len(values):
                anchor = f"#patents-item-{idx}"
        request.session[ITEM_LIST_SESSION_KEY] = values
        return HttpResponseRedirect(f"{url}{anchor}")

    errors = [
        [{"field_id": "patent", "message": "Enter a patent number or application"}] if not v.strip() else None
        for v in values
    ]
    request.session[ITEM_LIST_SESSION_KEY] = values

    if any(errors):
        ctx = _item_list_page_context(request, patent_values=values, patent_errors=errors)
        return render(request, "design_system/patterns/item_list.html", ctx)

    return HttpResponseRedirect(f"{url}#patents-list-anchor")


def item_list_htmx_update(request):
    """Apply an add or delete and return only the list, for the HTMX swap."""
    if request.method != "POST":
        return HttpResponse(status=405)

    try:
        count = min(int(request.POST.get("patents__count", 1)), ITEM_LIST_MAX)
    except (ValueError, TypeError):
        count = 1
    action = request.POST.get("patents__action", "")
    values = [request.POST.get(f"patent_{i}", "") for i in range(count)]

    if action == "add" and count < ITEM_LIST_MAX:
        values.append("")
    elif action.startswith("delete__"):
        idx = _parse_delete_idx(action)
        if idx is not None:
            try:
                values.pop(idx)
            except IndexError:
                pass
        if not values:
            values = [""]

    request.session[ITEM_LIST_SESSION_KEY] = values

    return render(
        request,
        "design_system/patterns/item_list_htmx_partial.html",
        {
            "count": len(values),
            "patent_values": values,
            "htmx_url": reverse("item_list_htmx"),
        },
    )


def error_summary_page(request):
    ctx = _nav_context_components(request, active_section="components", active_slug="error-summary")
    ctx["example_entries"] = [
        {"label": "Full name", "message": "Enter your full name", "anchor": "id_full_name"},
        {
            "label": "Email address",
            "message": "Enter an email address in the correct format, like name@example.com",
            "anchor": "id_email",
        },
    ]
    ctx["full_name_errors"] = ["Enter your full name"]
    ctx["email_errors"] = ["Enter an email address in the correct format, like name@example.com"]
    ctx["custom_title_entries"] = [
        {"label": "Date of birth", "message": "Enter a valid date of birth", "anchor": "id_dob"},
        {"label": "Phone number", "message": "Enter a UK phone number", "anchor": "id_phone"},
        {"label": "Postcode", "message": "Enter a full UK postcode", "anchor": "id_postcode"},
    ]
    return render(request, "design_system/components/error_summary.html", ctx)


def _whole_number_error(request, field_name, label, anchor):
    """Validate a posted step-comparison field, returning PLOS-style errors.

    Errors are only produced once the field has actually been submitted, so
    nothing shows on the initial GET. Each form posts only its own field, so a
    field not present in `request.POST` is treated as not yet submitted.
    """
    if request.method != "POST" or field_name not in request.POST:
        return []
    value = request.POST.get(field_name, "").strip()
    try:
        number = float(value)
    except ValueError:
        return [{"label": label, "message": "Enter a number", "anchor": anchor}]
    if number != int(number):
        return [{"label": label, "message": "Enter a whole number", "anchor": anchor}]
    return []


def text_input_page(request):
    ctx = _nav_context_components(request, active_section="components", active_slug="text-input")
    # Echo the posted value back into each field; both start empty so that
    # typing marks the value dirty (browsers skip step validation until a
    # number field has been user-modified).
    ctx["age_step_one_value"] = request.POST.get("age_step_one", "")
    ctx["age_step_any_value"] = request.POST.get("age_step_any", "")
    # The default-step input can reach the backend and render on-brand PLOS errors,
    # whereas the `step="1"` input is blocked by the browser before it can post.
    ctx["age_step_one_errors"] = _whole_number_error(request, "age_step_one", 'Age (step="1")', "id_age_step_one")
    ctx["age_step_any_errors"] = _whole_number_error(request, "age_step_any", "Age (default step)", "id_age_step_any")
    # Combined summary for the number section.
    ctx["number_errors"] = ctx["age_step_one_errors"] + ctx["age_step_any_errors"]
    return render(request, "design_system/components/text_input.html", ctx)


def design_system_component(request, component):
    slug = component.replace("-", "_")
    if component == "error-summary":
        return error_summary_page(request)
    if component == "text-input":
        return text_input_page(request)
    return render(
        request,
        f"design_system/components/{slug}.html",
        _nav_context_components(request, active_section="components", active_slug=component),
    )


def design_system_pattern(request, pattern):
    if pattern == "add-more":
        return add_more_htmx_page(request)
    if pattern == "item-list":
        return item_list_page(request)
    slug = pattern.replace("-", "_")
    return render(
        request,
        f"design_system/patterns/{slug}.html",
        _nav_context_patterns(request, active_section="patterns", active_slug=pattern),
    )
