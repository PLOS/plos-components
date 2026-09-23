from typing import Literal

from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_tag")
class Tag(PLOSBaseComponent):
    """
        A component that displays a short amount of text over a colored background to indicate the status of something
    """
    template_name = "tag.html"

    def get_context_data(
            self,
            color: Literal["grey", "green", "info", "teal", "blue", "purple", "magenta", "red", "orange", "yellow"] = "blue",
    ):
        return {
            "color":color
        }
