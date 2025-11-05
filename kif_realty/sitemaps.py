
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
            'index','about','properties','contact','blogs','retail','second',
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



class PropertySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    limit = 1000

    def items(self):
        all_properties = []
        page = 1

        while True:
            result = PropertyService.get_properties({'page': page})

            if not result.get('success') or not result.get('data'):
                break

            data = result['data']

            if isinstance(data, list):
                properties = data
                total_pages = 1
            elif isinstance(data, dict):
                properties = data.get('results') or data.get('data') or data.get('items') or []
                total_pages = data.get('total_pages', 1)
            else:
                properties = []
                total_pages = 1

            if not properties:
                break

            all_properties.extend(properties)

            if page >= total_pages:
                break

            page += 1

        return all_properties

    def location(self, obj):
        # 🧠 Handle both string and dict formats
        if isinstance(obj, dict):
            return f"/property/{obj.get('id')}/"
        elif isinstance(obj, str) or isinstance(obj, int):
            return f"/property/{obj}/"
        else:
            return "/property/"

    def lastmod(self, obj):
        if isinstance(obj, dict):
            return obj.get('updated_at')
        return None


