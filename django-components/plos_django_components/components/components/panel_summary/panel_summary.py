from typing import NamedTuple
from django_components import register

from ..base.base_component import PLOSBaseComponent

class PanelSummaryEntry(NamedTuple):
    title: str
    content: str


@register("plos_panel_summary")
class PanelSummary(PLOSBaseComponent):
    """
    Defines a panel component with summary information.

    Args:
        field_id (str, optional): An optional ID for the panel field.
        title (str): The title displayed in the panel.
        sections (list[dict]): A list of sections, where each section
          is a dictionary with an 'entries' key containing a list of entries. Each entry is a dictionary 
          with 'title' and 'content' keys.
    
    Usage:
        sections = [
            {
                "entries": [
                    {
                        "title": "Entry Title",
                        "content": "Entry Content"
                    },
                    {
                        "title": "Another Entry Title",
                        "content": "Another Entry Content"
                    }
                ]
            },
            {
                "entries": [
                    {
                        "title": "Third Entry Title",
                        "content": "Third Entry Content"
                    }
                ]
            }
        ]
        {% component "plos_panel_summary" title="Panel Summary Title" sections=sections %}

    """

    template_name = "panel_summary.html"

    def get_context_data(self, title: str, sections: list[dict] | None, field_id: str | None = None) -> dict:
        return {
            "field_id": field_id,
            "title": title,
            "sections": sections or [],
        }
