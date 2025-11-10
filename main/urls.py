from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    #Exclusive
    path('exclusive/', include('exclusive_properties.urls')),

    # path('model1/', views.model1, name='model1'),
    #  path('basenew/', views.basenw, name='basenew'),

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
    path('api/properties/filter/', views.filter_properties_api, name='filter_properties_api'),
    path('cities/', views.cities_api, name='cities_api'),  # Cities API for React frontend
    path('developers/', views.developers_api, name='developers_api'),  # Developers API for React frontend

    # Contact
    path('contact/', views.contact_view, name='contact'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),
    path('contact/ajax-submit/', views.contact_submit_ajax, name='contact_submit_ajax'),

    # Newsletter
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),

    path('privacy-policy/',views.privacy, name='privacy-policy'),
    path('terms&conditions/',views.terms, name='terms&conditions'),
    path('rera-compliance/',views.rera, name='rera-compliance'),

    # landingpages
    # ---------------KIF REALTY-------------
       
    path('retail',views.retail, name='retail'),
    path('second',views.second, name='second'),
    path('commercial',views.commercial, name='commercial'),
    path('luxury',views.luxury, name='luxury'),
    path('beach',views.beach, name='beach'),
    path('offplan',views.offplan, name='offplan'),
    path('labour',views.labour, name='labour'),
    path('warehouse',views.warehouse, name='warehouse'),
    path('plots',views.plots, name='plots'),
    path('mansions',views.mansions, name='mansions'),
]

