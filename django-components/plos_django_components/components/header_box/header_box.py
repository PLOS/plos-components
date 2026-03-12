from django_components import Component, register


@register("header_box")
class HeaderBox(Component):
    """
    Renders a full-width header.

    Args:
        text (str): The header text to display.
        level (int, optional): Header level, 1-4, corresponding to HTML <h1> to <h4>.
                               Defaults to 1. Levels outside this range raise an error.
    """
    template_name = "components/header_box/header_box.html"

    def get_context_data(self, text: str, level: int = 1):
        # Validate header level
        if not 1 <= level <= 4:
            raise ValueError(f"Invalid header level {level}: must be between 1 and 4")

        return {
            "text": text,
            "tag": f"h{level}",
        }
