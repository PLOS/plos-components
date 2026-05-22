from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_heading")
class Heading(PLOSBaseComponent):
    """
    Renders a heading.

    Args:
        level (int, optional): Heading level, 1-4, corresponding to HTML <h1> to <h4>.
                               Defaults to 1. Levels outside this range raise an error.
        css_class (str, optional): Overrides the default govuk-heading-{xl,l,m,s} class
                                   when a non-default heading style is needed (for example,
                                   govuk-error-summary__title inside the error summary box).
                                   When omitted, the level-based default is used.

    """

    template_name = "heading.html"

    def get_context_data(self, level: int = 1, css_class: str | None = None):  # noqa: D102
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
            "css_class": css_class if css_class is not None else heading_classes[level],
        }
