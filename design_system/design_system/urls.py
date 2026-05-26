from django.urls import include, path
urlpatterns = [
    path("", include("showcase.urls")),
    path("components/", include("django_components.urls")),
]
