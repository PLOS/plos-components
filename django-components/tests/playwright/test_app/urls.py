from django.urls import path
from plos_django_components.components.patterns.add_more.add_more import AddMore

from .views import add_more, text_input

urlpatterns = [
    path("patterns/add-more/", add_more.add_more_view, name="add_more"),
    path("patterns/add-more/patent-example/", add_more.patent_example_view, name="patent_example"),
    path("patterns/add-more/htmx/", AddMore.as_view(), name="add_more_htmx"),
    path("components/text-input/validation/", text_input.text_input_validation_view, name="text_input_validation"),
    path("components/text-input/types/", text_input.text_input_types_view, name="text_input_types"),
    path("components/text-input/attributes/", text_input.text_input_attributes_view, name="text_input_attributes"),
    path("components/text-input/visual/", text_input.text_input_visual_view, name="text_input_visual"),
    path("components/text-input/errors/", text_input.text_input_errors_view, name="text_input_errors"),
]
