from django_components import Component, register


@register("text_box")
class TextBox(Component):
    template_name = "text_box.html"

    def get_context_data(self, text: str):
        return {
            "text": text,
        }
