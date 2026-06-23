from django.shortcuts import render

from .utils.page_title import fetch_design_system_title_from_slug

STYLES = {"column-grid", "colour", "spacing", "typography"}

COMPONENTS = {
    "accordion",
    "back-link",
    "button",
    "text-input",
    "textarea",
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
}

PATTERNS = {
    "add-more",
    "check_answers",
}

ADD_MORE_SUBPAGES = [
    {"slug": "implementation", "label": "Implementation"},
]

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
    slug = pattern.replace("-", "_")
    return render(
        request,
        f"design_system/patterns/{slug}.html",
        _nav_context_patterns(request, active_section="patterns", active_slug=pattern),
    )
