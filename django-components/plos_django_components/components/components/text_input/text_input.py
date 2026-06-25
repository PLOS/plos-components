from typing import Literal

from django_components import register

from ....utils.govuk_helper import label_class_from_size
from ..base.base_component import PLOSBaseComponent


@register("plos_text_input")
class TextInput(PLOSBaseComponent):
    template_name = "text_input.html"

    def get_context_data(
        self,
        label,
        name,
        label_size: Literal["large", "medium", "small"] = "small",
        value: str | None = None,
        placeholder: str = "",
        required: bool = False,
        hint: str | None = None,
        errors: list[str] | None = None,
        input_type: Literal["text", "number", "password", "email", "url"] = "text",
        field_id: str | None = None,
        disabled: bool = False,
        autofocus: bool = False,
        maxlength: int | None = None,
        minlength: int | None = None,
        step: str | None = None,
        prefix: str | None = None,
        suffix: str | None = None,
    ):
        # Default `step` attribute to "any" for number inputs if not provided.
        # This removes browser validation as the default for step is `1`,
        # which meant that when users tried to submit decimal values in number inputs,
        # they would see non-PLOS error messages from the browser.
        if input_type == "number":
            step = step or "any"
        else:
            step = None

        # Normalize errors to a list of dictionaries for the error summary component
        normalized_errors = []
        for error in errors or []:
            if isinstance(error, str):
                normalized_errors.append({"message": error})
            else:
                normalized_errors.append(error)

        return {
            "label": label,
            "label_class": label_class_from_size(label_size),
            "input_type": input_type,
            "name": name,
            "value": value,
            "disabled": disabled,
            "autofocus": autofocus,
            "maxlength": maxlength,
            "minlength": minlength,
            "step": step,
            "placeholder": placeholder,
            "required": required,
            "hint": hint,
            "errors": normalized_errors,
            "id": field_id or f"id_{name}",
            "prefix": prefix,
            "suffix": suffix,
        }
