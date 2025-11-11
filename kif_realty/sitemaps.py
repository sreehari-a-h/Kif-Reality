
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.core.cache import cache
from main.models import BlogPost
import requests
import logging
import time
import math





logger = logging.getLogger(__name__)

# API Configuration
PROPERTIES_API_URL = 'http://54.197.194.173/api/properties/large/'
API_PROPERTIES_PER_PAGE = 50  # API returns 50 properties per page
SITEMAP_PROPERTIES_PER_PAGE = 250  # We want 250 properties per sitemap
CACHE_TIMEOUT = 3600  # 1 hour



# Static pages sitemap
class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return [
            'index',              # Homepage
            'about',              # About page
            'properties',         # Properties listing
            'contact',            # Contact page
            'blogs',              # Blogs listing
            
            # Landing pages
            'retail',
            'second',
            'commercial',
            'luxury',
            'beach',
            'offplan',
            'labour',
            'warehouse',
            'plots',
            'mansions',
            
            # Legal pages
            'privacy-policy',     # Privacy Policy
            'terms-conditions',   # Terms & Conditions
            'rera-compliance',    # RERA Compliance
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
# class PropertySitemap(Sitemap):
#     changefreq = 'daily'
#     priority = 0.9
#     limit = 50  # Number of properties per sitemap page (adjust as needed)

#     def items(self):
#         # Only fetch id, slug, updated_at to reduce memory usage
#         return Property.objects.filter(is_active=True).only(
#             'api_id', 'slug', 'updated_at', 'title'
#         ).order_by('-updated_at')

#     def lastmod(self, obj):
#         return obj.updated_at

#     def location(self, obj):
#         return obj.get_absolute_url()



# Base Property Sitemap Class
class BasePaginatedPropertySitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9
    protocol = 'https'
    
    def __init__(self, sitemap_page_number=1):
        """
        Initialize with sitemap page number
        Each sitemap page will contain 250 properties
        """
        self.sitemap_page_number = sitemap_page_number
        super().__init__()
    
    def items(self):
        """
        Fetch 250 properties for this sitemap page
        API returns 50 per page, so we need to fetch 5 API pages
        """
        cache_key = f'sitemap_properties_page_{self.sitemap_page_number}'
        cached_properties = cache.get(cache_key)
        
        if cached_properties:
            logger.info(f"[SITEMAP] Using cached properties for page {self.sitemap_page_number}: {len(cached_properties)} items")
            return cached_properties
        
        # Calculate which API pages we need to fetch
        # Sitemap page 1: API pages 1-5 (properties 1-250)
        # Sitemap page 2: API pages 6-10 (properties 251-500)
        # Sitemap page 3: API pages 11-15 (properties 501-750)
        # etc.
        
        api_pages_per_sitemap = SITEMAP_PROPERTIES_PER_PAGE // API_PROPERTIES_PER_PAGE  # 250 / 50 = 5
        start_api_page = ((self.sitemap_page_number - 1) * api_pages_per_sitemap) + 1
        end_api_page = start_api_page + api_pages_per_sitemap - 1
        
        properties = []
        
        try:
            print(f"\n🗺️ [SITEMAP PAGE {self.sitemap_page_number}] Fetching API pages {start_api_page}-{end_api_page}")
            logger.info(f"[SITEMAP] Page {self.sitemap_page_number}: Fetching API pages {start_api_page}-{end_api_page}")
            
            for api_page in range(start_api_page, end_api_page + 1):
                try:
                    print(f"  📄 API page {api_page}...", end=" ")
                    
                    response = requests.get(
                        PROPERTIES_API_URL,
                        params={'page': api_page},
                        timeout=30
                    )
                    
                    if response.status_code != 200:
                        print(f"❌ Error {response.status_code}")
                        continue
                    
                    data = response.json()
                    
                    if not data.get('status'):
                        print(f"⚠️ Status false")
                        continue
                    
                    data_block = data.get('data', {})
                    results = data_block.get('results', [])
                    
                    if not results:
                        print(f"⚠️ Empty")
                        break  # No more properties
                    
                    # Filter valid properties
                    valid_properties = [
                        prop for prop in results 
                        if isinstance(prop, dict) and prop.get('id') and prop.get('title')
                    ]
                    
                    properties.extend(valid_properties)
                    
                    print(f"✅ {len(valid_properties)} props | Total: {len(properties)}")
                    
                    time.sleep(0.2)  # Be nice to the API
                    
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
                    logger.error(f"[SITEMAP] Error fetching API page {api_page}: {str(e)}")
                    continue
            
            print(f"  ✅ Sitemap page {self.sitemap_page_number}: {len(properties)} properties")
            logger.info(f"[SITEMAP] Page {self.sitemap_page_number}: {len(properties)} properties")
            
            # Cache for 1 hour
            if properties:
                cache.set(cache_key, properties, CACHE_TIMEOUT)
            
            return properties
            
        except Exception as e:
            print(f"❌ FATAL ERROR: {str(e)}")
            logger.error(f"[SITEMAP] Fatal error on page {self.sitemap_page_number}: {str(e)}")
            return properties
    
    def location(self, obj):
        """Return the URL for each property"""
        if not isinstance(obj, dict):
            return None
        
        property_id = obj.get('id')
        if property_id:
            try:
                return reverse('property_detail', kwargs={'pk': int(property_id)})
            except (ValueError, TypeError):
                return None
        return None
    
    def lastmod(self, obj):
        """Return last modified date if available"""
        if not isinstance(obj, dict):
            return None
            
        from datetime import datetime
        
        date_field = obj.get('updated_at') or obj.get('modified_at')
        
        if date_field:
            try:
                if isinstance(date_field, str):
                    return datetime.fromisoformat(date_field.replace('Z', '+00:00'))
                return date_field
            except Exception:
                pass
        
        return None


# Create sitemap classes for each page
# With 1692 properties and 250 per page: 1692 / 250 = 6.768 → 7 pages

class PropertyPage1Sitemap(BasePaginatedPropertySitemap):
    """Properties 1-250 (API pages 1-5)"""
    def __init__(self):
        super().__init__(sitemap_page_number=1)


class PropertyPage2Sitemap(BasePaginatedPropertySitemap):
    """Properties 251-500 (API pages 6-10)"""
    def __init__(self):
        super().__init__(sitemap_page_number=2)


class PropertyPage3Sitemap(BasePaginatedPropertySitemap):
    """Properties 501-750 (API pages 11-15)"""
    def __init__(self):
        super().__init__(sitemap_page_number=3)


class PropertyPage4Sitemap(BasePaginatedPropertySitemap):
    """Properties 751-1000 (API pages 16-20)"""
    def __init__(self):
        super().__init__(sitemap_page_number=4)


class PropertyPage5Sitemap(BasePaginatedPropertySitemap):
    """Properties 1001-1250 (API pages 21-25)"""
    def __init__(self):
        super().__init__(sitemap_page_number=5)


class PropertyPage6Sitemap(BasePaginatedPropertySitemap):
    """Properties 1251-1500 (API pages 26-30)"""
    def __init__(self):
        super().__init__(sitemap_page_number=6)


class PropertyPage7Sitemap(BasePaginatedPropertySitemap):
    """Properties 1501-1692 (API pages 31-34)"""
    def __init__(self):
        super().__init__(sitemap_page_number=7)
