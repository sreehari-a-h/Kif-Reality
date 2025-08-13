from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('properties/', views.properties, name='properties'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('property/<int:property_id>/unit/<int:unit_id>/', views.unit_detail, name='unit_detail'),
    path('about/', views.about, name='about'),
    path('blogs/', views.blogs, name='blogs'),
    path('contact/', views.contact, name='contact'),
    path('api/newsletter/subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('api/search/', views.search_properties_api, name='search_properties_api'),
]
