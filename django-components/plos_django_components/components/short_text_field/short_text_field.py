from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("short_text_field")
class ShortTextField(PLOSBaseComponent):
    template_name = "short_text_field.html"

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
