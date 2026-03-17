from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("text_box")
class TextBox(PLOSBaseComponent):
    template_name = "text_box.html"

    def get_context_data(self, text: str):
        return {
            "text": text,
        }
