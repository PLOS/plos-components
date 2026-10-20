from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_panel")
class Panel(PLOSBaseComponent):
    """
    Defines a panel component.

    Args:
        title (str): The title displayed in the panel.

    """

    template_name = "panel.html"

    def get_context_data(self, title: str, field_id: str | None = None) -> dict:
        return {
            "field_id": field_id,
            "title": title,
        }
