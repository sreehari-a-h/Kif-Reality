# project/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from main.models import BlogPost
from main.services import PropertyService



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


class PropertySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        page = 1
        while True:
            result = PropertyService.get_properties({'page': page})
            if not result['success']:
                break

            properties = result['data'].get('results', [])
            if not properties:
                break

            for prop in properties:
                yield prop  # yield one property at a time

            total_pages = result['data'].get('total_pages', 1)
            if page >= total_pages:
                break

            page += 1

    def location(self, obj):
        return f"/property/{obj['id']}/"

    def lastmod(self, obj):
        # Optional: if the property dict has an 'updated_at' field
        return obj.get('updated_at')

