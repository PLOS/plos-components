from django_components import Component, register


@register("password_field")
class PasswordField(Component):
    template_name = "password_field.html"

    def get_context_data(self, label, name, value: str = "", placeholder: str = "", required: bool = False,
                         help_text: str = "", errors: list[str] | None = None,
                         field_id: str | None = None, disabled: bool = False, maxlength: int | None = None,
                         minlength: int | None = None, ):
        return {
            "label": label,
            "name": name,
            "value": value,
            "disabled": disabled,
            "maxlength": maxlength,
            "minlength": minlength,
            "placeholder": placeholder,
            "required": required,
            "help_text": help_text,
            "errors": errors or [],
            "id": field_id or f"id_{name}",
        }
