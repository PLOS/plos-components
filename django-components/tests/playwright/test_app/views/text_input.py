from django.shortcuts import render


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

    return render(request, "playwright_test_app/text_input/text_input_validation.html", context)
