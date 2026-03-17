from typing import Literal

from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_text_input")
class TextInput(PLOSBaseComponent):
    template_name = "text_input.html"

    def get_context_data(self, label, name, value: str = "", placeholder: str = "", required: bool = False,
                         hint: str | None = None, errors: list[str] | None = None,
                         input_type: Literal["text", "number", "password", "email", "url"] = "text",
                         field_id: str | None = None, disabled: bool = False, maxlength: int | None = None,
                         minlength: int | None = None, prefix: str | None = None, suffix: str | None = None,):
        return {
            "label": label,
            "input_type": input_type,
            "name": name,
            "value": value,
            "disabled": disabled,
            "maxlength": maxlength,
            "minlength": minlength,
            "placeholder": placeholder,
            "required": required,
            "hint": hint,
            "errors": errors or [],
            "id": field_id or f"id_{name}",
            "prefix": prefix,
            "suffix": suffix,
        }
