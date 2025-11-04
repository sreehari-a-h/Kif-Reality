# project/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from main.models import BlogPost
from exclusive_properties.models import ExclusiveProperty


# Static pages sitemap
class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    # List all the named URL patterns for static and landing pages
    def items(self):
        return [
            'index','about','properties','contact','blogs','model1','basenew','retail','second','commercial','luxury','beach','offplan','labour','warehouse','plots','mansions',
        ]

    def location(self, item):
        return reverse(item)


# Blog sitemap
class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return BlogPost.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('blog_detail', kwargs={'slug': obj.slug})

# ExclusiveProperty sitemap
class ExclusivePropertySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return ExclusiveProperty.objects.filter(status="available")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('exclusive_properties:detail', kwargs={'slug': obj.slug})


