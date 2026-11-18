"""
A horizontal rule that separates sections of content.
"""

from django_components import register

from ..base.base_component import PLOSBaseComponent

SIZES = ("m", "l", "xl")


@register("plos_section_break")
class SectionBreak(PLOSBaseComponent):
    """
    Renders a section break (a styled <hr>).

    Parameters:

        size     vertical margin: "m", "l", "xl" or "" for none (default: "l")
        visible  draw a visible rule (default: True)

    Example usage:

        {% component "plos_section_break" / %}
        {% component "plos_section_break" size="m" visible=False / %}
    """

    template_name = "section_break.html"

    def get_context_data(self, size: str = "l", visible: bool = True):
        if size and size not in SIZES:
            raise ValueError(f"size must be one of {SIZES} or empty, got {size!r}.")
        return {
            "size": size,
            "visible": visible,
        }
