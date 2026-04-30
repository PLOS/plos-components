from django.urls import path

from . import views

urlpatterns = [
    path("text-input/", views.text_input_view, name="text_input"),
]
