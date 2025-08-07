from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('properties/', views.properties, name='properties'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('api/newsletter/subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('api/search/', views.search_properties_api, name='search_properties_api'),
]
