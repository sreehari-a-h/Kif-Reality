from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemaps import BlogSitemap, ExclusivePropertySitemap, StaticViewSitemap




sitemaps_dict = {
    'blogs':BlogSitemap,
    'exclusive_properties': ExclusivePropertySitemap,
    'static':StaticViewSitemap
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps_dict}, name='django.contrib.sitemaps.views.sitemap'),

    path('tinymce/', include('tinymce.urls')),
    path('exclusive-properties/', include('exclusive_properties.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

