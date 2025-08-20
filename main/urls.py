from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    #Exclusive
    path('exclusive/', include('exclusive_properties.urls')),

    path('model/', views.model, name='model'),
    path('model1/', views.model1, name='model1'),
    path('model2/', views.model2, name='model2'),
    path('model3/', views.model3, name='model3'),
    path('model4/', views.model4, name='model4'),
    path('model5/', views.model5, name='model5'),
    path('model6/', views.model6, name='model6'),
    path('model7/', views.model7, name='model7'),
    path('model8/', views.model8, name='model8'),
    path('model9/', views.model9, name='model9'),

    # Properties
    path('properties/', views.properties, name='properties'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('property/<int:property_id>/unit/<int:unit_id>/', views.unit_detail, name='unit_detail'),

    # Static pages
    path('about/', views.about, name='about'),

    # Blogs
    path('blogs/', views.blog_list, name='blogs'),
    path('blogs/search/', views.blog_search, name='blog_search'),
    path('blogs/category/<slug:slug>/', views.blog_category, name='blog_category'),
    path('blogs/tag/<slug:slug>/', views.blog_tag, name='blog_tag'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),

    # API
    path('api/newsletter/subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('api/search/', views.search_properties_api, name='search_properties_api'),

    # Contact
    path('contact/', views.contact_view, name='contact'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),
    path('contact/ajax-submit/', views.contact_submit_ajax, name='contact_submit_ajax'),

    # Newsletter
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]

