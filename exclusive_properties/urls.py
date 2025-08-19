from django.urls import path
from . import views

app_name = 'exclusive_properties'

urlpatterns = [
    path('', views.exclusive_properties_list, name='list'),
    path('api/', views.exclusive_properties_api, name='api'),
    path('inquiry/', views.submit_property_inquiry, name='submit_inquiry'),
    path('<slug:slug>/', views.exclusive_property_detail, name='detail'),
]