from django_components import Component, register


@register("textarea")
class Textarea(Component):
    template_name = "textarea.html"

    def get_context_data(
        self,
        id: str,
        name: str,
        label: str,
        hint: str | None = None,
        value: str = "",
        rows: int = 5,
        maxlength: int | None = None,
        errors: list[str] | None = None,
    ):
        return {
            "id": id,
            "name": name,
            "label": label,
            "hint": hint,
            "value": value,
            "rows": rows,
            "maxlength": maxlength,
            "errors": errors or [],
        }
