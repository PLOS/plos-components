"""
Component for rendering a checkmark within a green circle icon.
"""


from django_components import register

from ...base.base_component import PLOSBaseComponent


@register("plos_icon_circle_check")
class CircleCheckIcon(PLOSBaseComponent):
    """
    Renders a checkmark within a green circle icon.

    Args:
        size (str, optional): Icon size. One of xs, sm, md, lg, xl.
                              Defaults to md (24px). Passed through to plos_icon_base.
        display (str, optional): Defines the CSS display mode.
                                 Defaults to inline. Passed through to plos_icon_base.

    """

    template_name = "circle_check_icon.html"

    def get_context_data(  # noqa: D102
            self,
            size: str = "md",
            display: str = "inline",
            field_id: str | None = None
        ):
        return {
            "size": size,
            "display": display,
            "field_id": field_id
        }
