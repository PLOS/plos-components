from typing import Literal

from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_textarea")
class Textarea(PLOSBaseComponent):
    template_name = "textarea.html"

    def get_context_data(
        self,
        id: str,
        name: str,
        label: str | None = None,
        label_size: Literal["large", "medium", "small"] = "small",
        hint: str | None = None,
        placeholder: str | None = None,
        required: bool = False,
        value: str | None = None,
        rows: int = 5,
        cols: int | None = None,
        maxlength: int | None = None,
        minlength: int | None = None,
        errors: list[str] | None = None,
    ):
        return {
            "id": id,
            "name": name,
            "label": label,
            "label_size": label_size,
            "hint": hint,
            "placeholder": placeholder,
            "required": required,
            "value": value,
            "rows": rows,
            "cols": cols,
            "maxlength": maxlength,
            "minlength": minlength,
            "errors": errors or [],
        }
