"""
URL configuration for the Playwright test application.
"""

from django.urls import path

from .views import text_input
from .views.icon.icon_views import icon_showcase_view

urlpatterns = [
    path("components/text-input/validation/", text_input.text_input_validation_view, name="text_input_validation"),
    path("components/text-input/types/", text_input.text_input_types_view, name="text_input_types"),
    path("components/text-input/attributes/", text_input.text_input_attributes_view, name="text_input_attributes"),
    path("components/text-input/visual/", text_input.text_input_visual_view, name="text_input_visual"),
    path("components/text-input/errors/", text_input.text_input_errors_view, name="text_input_errors"),
    path("components/icon/showcase/", icon_showcase_view, name="icon_showcase"),
]
