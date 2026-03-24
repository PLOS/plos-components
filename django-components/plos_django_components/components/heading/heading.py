from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_heading")
class Heading(PLOSBaseComponent):
    """
    Renders a heading.

    Args:
        level (int, optional): Heading level, 1-4, corresponding to HTML <h1> to <h4>.
                               Defaults to 1. Levels outside this range raise an error.

    """

    template_name = "heading.html"

    def get_context_data(self, level: int = 1):  # noqa: D102
        # Validate heading level
        if not 1 <= level <= 4:
            raise ValueError(f"Invalid heading level {level}: must be between 1 and 4")

        heading_classes = {
            1: "govuk-heading-xl",
            2: "govuk-heading-l",
            3: "govuk-heading-m",
            4: "govuk-heading-s",
        }

        return {
            "tag": f"h{level}",
            "css_class": heading_classes[level],
        }
