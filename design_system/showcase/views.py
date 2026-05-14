from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .utils.page_title import fetch_design_system_title_from_slug

STYLES = {"column-grid", "colour", "spacing", "typography"}

COMPONENTS = {
    "accordion",
    "button",
    "text-input",
    "textarea",
    "select",
    "error-summary",
    "panel",
    "radios",
    "checkboxes",
    "banner",
    "add-more",
    "summary-list",
    "date_input",
}

PATTERNS = {
    "check_answers",
}

TYPOGRAPHY_SUBPAGES = [
    {"slug": "headings-body", "label": "Headings and Body"},
    {"slug": "functional-text", "label": "Functional Text"},
]

SESSION_KEY_ADD_MORE = "ds_add_more_patents"
SESSION_KEY_ADD_MORE_HTMX = "ds_add_more_htmx_patents"
ADD_MORE_MAX = 10


def _parse_delete_idx(action):
    try:
        return int(action.split("__")[1])
    except (IndexError, ValueError):
        return None


def _nav_context_components(
    request, active_section=None, active_slug=None, active_subslug=None
):
    return _nav_context(
        request, active_section, active_slug, active_subslug, COMPONENTS
    )


def _nav_context_patterns(
    request, active_section=None, active_slug=None, active_subslug=None
):
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
        nav_components = [
            {"slug": c, "label": fetch_design_system_title_from_slug(c)}
            for c in sorted(library)
        ]

    return {
        "nav_styles": nav_styles,
        "nav_components": nav_components,
        "active_section": active_section,
        "active_slug": active_slug,
        "active_subslug": active_subslug,
        "current_path": request.path,
    }


def _build_page_context(request, patents_values=None, patents_errors=None):
    if patents_values is None:
        saved = request.session.get(SESSION_KEY_ADD_MORE_HTMX, None)
        if saved is None:
            saved = [""]
            request.session[SESSION_KEY_ADD_MORE_HTMX] = saved
        patents_values = saved

    ctx = _nav_context_components(
        request, active_section="components", active_slug="add-more"
    )
    ctx["count"] = len(patents_values)
    ctx["patent_values"] = patents_values
    ctx["htmx_url"] = reverse("add_more_htmx_update", kwargs={"list_name": "patents"})
    if patents_errors is not None:
        ctx["errors"] = patents_errors

    return ctx


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
    if request.method == "POST" and not request.headers.get("HX-Request"):
        return _handle_patents_post(request)
    return render(
        request, "design_system/components/add_more.html", _build_page_context(request)
    )


def _handle_patents_post(request):
    saved = request.session.get(SESSION_KEY_ADD_MORE_HTMX, [""])
    try:
        count = min(int(request.POST.get("patents__count", len(saved))), ADD_MORE_MAX)
    except (ValueError, TypeError):
        count = len(saved)
    values = [request.POST.get(f"patent_{i}", "") for i in range(count)]
    action = request.POST.get("patents__action", "")

    if action == "add" or action.startswith("delete__"):
        anchor = "#patents-list-anchor"
        if action == "add" and count < ADD_MORE_MAX:
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
            new_count = len(values)
            if idx is not None and idx < new_count:
                anchor = f"#patents-item-{idx}"
        request.session[SESSION_KEY_ADD_MORE_HTMX] = values
        url = reverse("design_system_component", kwargs={"component": "add-more"})
        return HttpResponseRedirect(f"{url}{anchor}")

    errors = [
        [{"field_id": "patent", "message": "Enter a patent number or application"}]
        if not v.strip()
        else None
        for v in values
    ]
    request.session[SESSION_KEY_ADD_MORE_HTMX] = values

    if any(errors):
        ctx = _build_page_context(request, patents_values=values, patents_errors=errors)
        return render(request, "design_system/components/add_more.html", ctx)

    url = reverse("design_system_component", kwargs={"component": "add-more"})
    return HttpResponseRedirect(f"{url}#patents-list-anchor")


def add_more_htmx_update(request, list_name):
    if request.method != "POST":
        return HttpResponse(status=405)

    if list_name == "patents":
        try:
            count = int(request.POST.get("patents__count", 1))
        except (ValueError, TypeError):
            count = 1
        action = request.POST.get("patents__action", "")
        values = [request.POST.get(f"patent_{i}", "") for i in range(count)]

        if action == "add" and count < ADD_MORE_MAX:
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

        request.session[SESSION_KEY_ADD_MORE_HTMX] = values
        count = len(values)

        return render(
            request,
            "design_system/components/add_more_htmx_partial.html",
            {
                "count": count,
                "patent_values": values,
                "htmx_url": reverse(
                    "add_more_htmx_update", kwargs={"list_name": list_name}
                ),
            },
        )

    raise Http404


def error_summary_page(request):
    ctx = _nav_context_components(
        request, active_section="components", active_slug="error-summary"
    )
    ctx["example_entries"] = [
        {"label": "Full name", "message": "Enter your full name", "anchor": "id_full_name"},
        {"label": "Email address", "message": "Enter an email address in the correct format, like name@example.com", "anchor": "id_email"},
    ]
    ctx["full_name_errors"] = ["Enter your full name"]
    ctx["email_errors"] = ["Enter an email address in the correct format, like name@example.com"]
    ctx["custom_title_entries"] = [
        {"label": "Date of birth", "message": "Enter a valid date of birth", "anchor": "id_dob"},
        {"label": "Phone number", "message": "Enter a UK phone number", "anchor": "id_phone"},
        {"label": "Postcode", "message": "Enter a full UK postcode", "anchor": "id_postcode"},
    ]
    return render(request, "design_system/components/error_summary.html", ctx)


def design_system_component(request, component):
    if component == "add-more":
        return add_more_htmx_page(request)
    if component == "error-summary":
        return error_summary_page(request)
    slug = component.replace("-", "_")
    return render(
        request,
        f"design_system/components/{slug}.html",
        _nav_context_components(
            request, active_section="components", active_slug=component
        ),
    )


def design_system_pattern(request, pattern):
    slug = pattern.replace("-", "_")
    return render(
        request,
        f"design_system/patterns/{slug}.html",
        _nav_context_patterns(request, active_section="patterns", active_slug=pattern),
    )
