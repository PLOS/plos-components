"""
File upload component with drag-and-drop support.

This component is UI-only. It does not handle file submission. The file
is submitted as part of the surrounding HTML form, and the destination
is determined by that form's action attribute. Server-side handling is
the responsibility of the implementing service.
"""

from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_file_upload")
class FileUpload(PLOSBaseComponent):
    """
    File upload component with drag-and-drop support.
    """

    template_name = "file_upload.html"

    def get_context_data(  # noqa: D102
        self,
        field_id: str,
        name: str,
        label: str,
        hint: str | None = None,  # None = not shown
        multiple: bool = True,  # True = allow multiple file selection
        accept: str | None = None,  # None = any file type
        disabled: bool = False,  # False = enabled
        errors: list[str] | None = None,  # None = no errors shown
    ):
        return {
            "field_id": field_id,
            "name": name,
            "label": label,
            "hint": hint,
            "multiple": multiple,
            "accept": accept,
            "disabled": disabled,
            "errors": errors or [],
        }
