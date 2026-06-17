from django.shortcuts import render


def add_more_view(request):
    return render(request, "playwright_test_app/add_more.html")


def patent_example_view(request):
    from plos_django_components.components.patterns.add_more.add_more import get_session_key_values

    # Simulate a database
    database = [
        {"patent_number": "123", "patent_description": "First patent"},
        {"patent_number": "456", "patent_description": "Second patent"},
    ]

    # Use session to store "saved" data for the test to verify
    if "saved_patents" not in request.session:
        request.session["saved_patents"] = database

    saved_data = None

    if request.method == "POST":
        if "save_action" in request.POST:
            count = int(request.POST.get("patents__count", "0"))
            items = []
            for i in range(count):
                number = request.POST.get(f"patent_number_{i}")
                description = request.POST.get(f"patent_description_{i}")
                if number or description:
                    items.append(
                        {
                            "patent_number": number,
                            "patent_description": description,
                        }
                    )

            request.session["saved_patents"] = items
            saved_data = items
            # Clear AddMore session
            request.session[get_session_key_values("patents")] = None

    # Handle malformed data scenario via query param
    if request.GET.get("malformed") == "true":
        values = ["this is not a dict"]
    elif request.GET.get("empty") == "true":
        values = []
    else:
        values = request.session.get("saved_patents", database)

    context = {
        "saved_data": saved_data,
        "values": values,
        "additional_buttons": [
            {
                "label": "Save All Patents",
                "button_type": "submit",
                "field_name": "save_action",
                "form_action": "",
            }
        ],
    }
    return render(request, "playwright_test_app/patent_example.html", context)


def text_input_validation_view(request):
    context = {
        "age_step_one_value": "",
        "age_step_one_errors": [],
        "age_step_any_value": "",
        "age_step_any_errors": [],
        "errors": [],
        "success_msg": "",
    }

    if request.method == "POST":
        if "age_step_one" in request.POST:
            value = request.POST.get("age_step_one")
            context["age_step_one_value"] = value
            # In a real app, we'd validate here.
            # If we reach here, it means the browser didn't block it.
            context["success_msg"] = f"Submitted step_one with value: {value}"
            try:
                float_val = float(value)
                if float_val != int(float_val):
                    context["age_step_one_errors"] = [
                        {
                            "label": "How many patents do you have?",
                            "message": "Enter a whole number",
                            "anchor": "id_age_step_one",
                        }
                    ]
                    context["errors"] = context["age_step_one_errors"]
            except ValueError:
                pass

        elif "age_step_any" in request.POST:
            value = request.POST.get("age_step_any")
            context["age_step_any_value"] = value
            context["success_msg"] = f"Submitted step_any with value: {value}"
            try:
                float_val = float(value)
                if float_val != int(float_val):
                    context["age_step_any_errors"] = [
                        {
                            "label": "How many patents do you have?",
                            "message": "Enter a whole number",
                            "anchor": "id_age_step_any",
                        }
                    ]
                    context["errors"] = context["age_step_any_errors"]
            except ValueError:
                pass

    return render(request, "playwright_test_app/text_input_validation.html", context)
