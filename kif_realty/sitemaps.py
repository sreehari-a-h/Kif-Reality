# project/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from main.models import BlogPost
from main.services import PropertyService


# Static pages sitemap
class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return [
            'index','about','properties','contact','blogs','model1','basenew','retail','second',
            'commercial','luxury','beach','offplan','labour','warehouse','plots','mansions',
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


# Property sitemap with limit support
class PropertySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    limit = 1000  # Django will split sitemap into files of 1000 items each

    def items(self):
        """Fetch all properties from PropertyService."""
        all_properties = []
        page = 1

        while True:
            result = PropertyService.get_properties({'page': page})
            if not result['success']:
                break

            properties = result['data'].get('results', [])
            if not properties:
                break

            all_properties.extend(properties)

            total_pages = result['data'].get('total_pages', 1)
            if page >= total_pages:
                break

            page += 1

        return all_properties  # Must return a list, not a generator

    def location(self, obj):
        return f"/property/{obj['id']}/"

    def lastmod(self, obj):
        return obj.get('updated_at')
