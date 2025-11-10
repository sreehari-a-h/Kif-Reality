from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap, index as sitemap_index
from .sitemaps import BlogSitemap, StaticViewSitemap, PropertySitemap
from django.views.generic import TemplateView
from main import views as main_views  # import your app's views


sitemaps_dict = {
    'blogs': BlogSitemap,
    'properties': PropertySitemap,   # This will be automatically paginated
    'static': StaticViewSitemap     
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('exclusive-properties/', include('exclusive_properties.urls')),
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