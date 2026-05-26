"""
A component which renders an error summary.

Use at the top of a form page to collect and display validation errors with
anchor links to the affected fields.
"""
from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_error_summary")
class ErrorSummary(PLOSBaseComponent):
    """
    Renders an error summary box linking to field-level errors.

    Each entry in `entries` is a dict with three keys:

        label: human-readable label shown before the colon (e.g. "Patent 1")
        message: the error text (e.g. "Enter a patent number")
        anchor: the id of the target input, without the leading # (e.g. "patent_0")

    The component renders nothing when `entries` is empty.

    Optional parameters:

        title   heading inside the error summary box (default: "There is an issue")

    Example usage:

        entries = [
            {"label": "Full name", "message": "Enter your full name", "anchor": "id_full_name"},
        ]
        {% component "plos_error_summary" entries=entries %}{% endcomponent %}
    """

    template_name = "error_summary.html"

    def get_context_data(
        self,
        entries: list[dict] | None = None,
        title: str = "There is an issue",
    ):
        safe_entries = entries or []
        return {
            "entries": safe_entries,
            "title": title,
            "has_entries": bool(safe_entries),
        }
