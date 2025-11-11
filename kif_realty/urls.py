from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap, index as sitemap_index
# from .sitemaps import BlogSitemap, StaticViewSitemap, PropertySitemap
from .sitemaps import (
    BlogSitemap, 
    StaticViewSitemap, 
    PropertyPage1Sitemap,
    PropertyPage2Sitemap,
    PropertyPage3Sitemap,
    PropertyPage4Sitemap,
    PropertyPage5Sitemap,
    PropertyPage6Sitemap,
    PropertyPage7Sitemap,
)
from main import views as main_views  # import your app's views


sitemaps_dict = {
    'blogs': BlogSitemap,
    'properties-1': PropertyPage1Sitemap,  # Properties 1-250
    'properties-2': PropertyPage2Sitemap,  # Properties 251-500
    'properties-3': PropertyPage3Sitemap,  # Properties 501-750
    'properties-4': PropertyPage4Sitemap,  # Properties 751-1000
    'properties-5': PropertyPage5Sitemap,  # Properties 1001-1250
    'properties-6': PropertyPage6Sitemap,  # Properties 1251-1500
    'properties-7': PropertyPage7Sitemap,  # Properties 1501-1692  
    'static': StaticViewSitemap     
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('tinymce/', include('tinymce.urls')),
    # path('exclusive-properties/', include('exclusive_properties.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # Sitemap index (main sitemap file)
    path('sitemap.xml', sitemap_index, {'sitemaps': sitemaps_dict}, name='django.contrib.sitemaps.views.index'),
    
    # Individual sitemap sections
    path('sitemap-<section>.xml', sitemap, {'sitemaps': sitemaps_dict}, name='django.contrib.sitemaps.views.sitemap'),
    
    # Robots.txt
    path('robots.txt', main_views.robots_txt, name='robots_txt'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)