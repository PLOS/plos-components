from django.urls import path

from . import views

urlpatterns = [
    path('', views.design_system_index, name='design_system_index'),
    path('styles/', views.design_system_styles_index, name='design_system_styles_index'),
    path('styles/typography/<str:page>/', views.design_system_typography, name='design_system_typography'),
    path('styles/<str:page>/', views.design_system_style, name='design_system_style'),
    path('components/', views.design_system_components_index, name='design_system_components_index'),
    path('update-list/<str:list_name>/', views.item_list_htmx_update, name='item_list_htmx_update'),
    path('components/<str:component>/', views.design_system_component, name='design_system_component'),
]
