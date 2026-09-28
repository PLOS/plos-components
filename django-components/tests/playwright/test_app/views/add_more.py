from django.shortcuts import render
from plos_django_components.components.patterns.add_more.logic import (
    apply_add_or_delete,
    collapsed_after_add_or_delete,
    error_summary_entries,
    posted_count,
)

MAX_ITEMS = 3


def add_more_view(request):
    values = [""]
    errors = None
    collapsed = []
    action = ""
    saved = []

    if request.method == "POST":
        count = posted_count(request.POST, "patents", MAX_ITEMS)
        values = [request.POST.get(f"patent_{i}", "") for i in range(count)]
        action = request.POST.get("patents__action", "")
        if action:
            values = apply_add_or_delete(values, action, MAX_ITEMS)
            collapsed = collapsed_after_add_or_delete(request.POST, "patents", action)
        else:
            errors = [
                None if v.strip() else [{"field_id": "patent", "message": "Enter a patent number"}] for v in values
            ]
            if not any(errors):
                saved = values

    context = {
        "values": values,
        "errors": errors,
        "error_summary": error_summary_entries(errors, "patent"),
        "collapsed": collapsed,
        "last_action": action,
        "max_items": MAX_ITEMS,
        "saved": saved,
        "add_more_url": request.path,
    }
    return render(request, "playwright_test_app/add_more/add_more.html", context)
