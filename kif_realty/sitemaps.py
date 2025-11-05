
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from main.models import BlogPost



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




