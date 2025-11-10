
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from main.models import BlogPost, Property



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



# class PropertySitemap(Sitemap):
#     changefreq = 'daily'
#     priority = 0.9

#     def items(self):
#         return Property.objects.filter(is_active=True)

#     def lastmod(self, obj):
#         return obj.updated_at

#     def location(self, obj):
#         return obj.get_absolute_url()
    
    
    
# Property sitemap with pagination (50 properties per page)
class PropertySitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9
    limit = 50  # Number of properties per sitemap page (adjust as needed)

    def items(self):
        # Only fetch id, slug, updated_at to reduce memory usage
        return Property.objects.filter(is_active=True).only(
            'api_id', 'slug', 'updated_at', 'title'
        ).order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()
