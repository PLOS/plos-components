from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_header_box")
class HeaderBox(PLOSBaseComponent):
    """
    Renders a full-width header.

    Args:
        level (int, optional): Header level, 1-4, corresponding to HTML <h1> to <h4>.
                               Defaults to 1. Levels outside this range raise an error.

    """

    template_name = "header_box.html"

    def get_context_data(self, level: int = 1):  # noqa: D102
        # Validate header level
        if not 1 <= level <= 4:
            raise ValueError(f"Invalid header level {level}: must be between 1 and 4")

        return {
            "tag": f"h{level}",
        }
