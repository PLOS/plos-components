from django.urls import path
from plos_django_components.components.patterns.add_more.add_more import AddMore

from . import views

urlpatterns = [
    path("", views.design_system_index, name="design_system_index"),
    path(
        "styles/", views.design_system_styles_index, name="design_system_styles_index"
    ),
    path(
        "styles/typography/<str:page>/",
        views.design_system_typography,
        name="design_system_typography",
    ),
    path("styles/<str:page>/", views.design_system_style, name="design_system_style"),
    path(
        "components/",
        views.design_system_components_index,
        name="design_system_components_index",
    ),
    path(
        "patterns/",
        views.design_system_patterns_index,
        name="design_system_patterns_index",
    ),
    path(
        "components/<str:component>/",
        views.design_system_component,
        name="design_system_component",
    ),
    path(
        "patterns/add-more/htmx/",
        AddMore.as_view(),
        name="add_more_htmx",
    ),
    path(
        "patterns/<str:pattern>/",
        views.design_system_pattern,
        name="design_system_pattern",
    ),
]
