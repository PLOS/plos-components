from django.urls import path

from plos_django_components.components.patterns.add_more.add_more import AddMore

from . import views

urlpatterns = [
    path("patterns/add-more/", views.add_more_view, name="add_more"),
    path("patterns/add-more/patent-example/", views.patent_example_view, name="patent_example"),
    path("patterns/add-more/htmx/", AddMore.as_view(), name="add_more_htmx"),
]
