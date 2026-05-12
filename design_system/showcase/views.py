from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

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
    "item-list",
    "summary-list",
    "check_answers",
}

TYPOGRAPHY_SUBPAGES = [
    {"slug": "headings-body", "label": "Headings and Body"},
    {"slug": "functional-text", "label": "Functional Text"},
]

SESSION_KEY_ITEM_LIST = "ds_item_list_patents"
SESSION_KEY_ITEM_LIST_HTMX = "ds_item_list_htmx_patents"
ITEM_LIST_MAX = 10


def _parse_delete_idx(action):
    try:
        return int(action.split("__")[1])
    except (IndexError, ValueError):
        return None


def _nav_context(request, active_section=None, active_slug=None, active_subslug=None):
    nav_styles = []
    for s in sorted(STYLES):
        item = {"slug": s, "label": s.replace("-", " ").title(), "children": []}
        if s == "typography":
            item["children"] = TYPOGRAPHY_SUBPAGES
        nav_styles.append(item)

    return {
        "nav_styles": nav_styles,
        "nav_components": [
            {"slug": c, "label": c.replace("-", " ").title()}
            for c in sorted(COMPONENTS)
        ],
        "active_section": active_section,
        "active_slug": active_slug,
        "active_subslug": active_subslug,
        "current_path": request.path,
    }


def _build_page_context(request, patents_values=None, patents_errors=None):
    if patents_values is None:
        saved = request.session.get(SESSION_KEY_ITEM_LIST_HTMX, None)
        if saved is None:
            saved = [""]
            request.session[SESSION_KEY_ITEM_LIST_HTMX] = saved
        patents_values = saved

    ctx = _nav_context(request, active_section="components", active_slug="item-list")
    ctx["count"] = len(patents_values)
    ctx["patent_values"] = patents_values
    ctx["htmx_url"] = reverse("item_list_htmx_update", kwargs={"list_name": "patents"})
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
    ctx = _nav_context(request, active_section="components")
    ctx["components"] = ctx["nav_components"]
    return render(request, "design_system/components/index.html", ctx)


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


def item_list_htmx_page(request):
    if request.method == "POST" and not request.headers.get("HX-Request"):
        return _handle_patents_post(request)
    return render(
        request, "design_system/components/item_list.html", _build_page_context(request)
    )


def _handle_patents_post(request):
    saved = request.session.get(SESSION_KEY_ITEM_LIST_HTMX, [""])
    try:
        count = min(int(request.POST.get("patents__count", len(saved))), ITEM_LIST_MAX)
    except (ValueError, TypeError):
        count = len(saved)
    values = [request.POST.get(f"patent_{i}", "") for i in range(count)]
    action = request.POST.get("patents__action", "")

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
            new_count = len(values)
            if idx is not None and idx < new_count:
                anchor = f"#patents-item-{idx}"
        request.session[SESSION_KEY_ITEM_LIST_HTMX] = values
        url = reverse("design_system_component", kwargs={"component": "item-list"})
        return HttpResponseRedirect(f"{url}{anchor}")

    errors = [
        [{"field_id": "patent", "message": "Enter a patent number or application"}]
        if not v.strip()
        else None
        for v in values
    ]
    request.session[SESSION_KEY_ITEM_LIST_HTMX] = values

    if any(errors):
        ctx = _build_page_context(request, patents_values=values, patents_errors=errors)
        return render(request, "design_system/components/item_list.html", ctx)

    url = reverse("design_system_component", kwargs={"component": "item-list"})
    return HttpResponseRedirect(f"{url}#patents-list-anchor")


def item_list_htmx_update(request, list_name):
    if request.method != "POST":
        return HttpResponse(status=405)

    if list_name == "patents":
        try:
            count = int(request.POST.get("patents__count", 1))
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

        request.session[SESSION_KEY_ITEM_LIST_HTMX] = values
        count = len(values)

        return render(
            request,
            "design_system/components/item_list_htmx_partial.html",
            {
                "count": count,
                "patent_values": values,
                "htmx_url": reverse(
                    "item_list_htmx_update", kwargs={"list_name": list_name}
                ),
            },
        )

    raise Http404


def design_system_component(request, component):
    if component == "item-list":
        return item_list_htmx_page(request)
    slug = component.replace("-", "_")
    return render(
        request,
        f"design_system/components/{slug}.html",
        _nav_context(request, active_section="components", active_slug=component),
    )
