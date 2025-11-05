from django.contrib.sitemaps import Sitemap
from django.core.cache import cache
from main.services import PropertyService
import logging

logger = logging.getLogger(__name__)

class PropertySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    limit = 5000
    
    def items(self):
        cache_key = 'property_sitemap_items'
        cached_items = cache.get(cache_key)
        if cached_items:
            logger.info(f"✅ Using cached property items ({len(cached_items)})")
            return cached_items
        
        all_properties = []
        page = 1
        max_pages = 100
        
        while page <= max_pages:
            try:
                logger.info(f"📦 Fetching property page {page}")
                result = PropertyService.get_properties({'page': page})
                
                # Ensure result is valid
                if not isinstance(result, dict) or not result.get('success'):
                    logger.warning(f"⚠️ API failed on page {page}")
                    break
                
                data = result.get('data')
                if not data:
                    logger.warning(f"⚠️ No data found on page {page}")
                    break
                
                # Extract property list
                properties = None
                if isinstance(data, dict):
                    for key in ['results', 'data', 'items', 'properties', 'property_list']:
                        if key in data and isinstance(data[key], list):
                            properties = data[key]
                            logger.info(f"✅ Found properties in '{key}' key")
                            break
                elif isinstance(data, list):
                    properties = data
                    logger.info(f"✅ Data itself is the properties list")
                
                if not properties or not isinstance(properties, list):
                    logger.info(f"🛑 No properties found on page {page}")
                    break
                
                # Stop if empty list (no more results)
                if len(properties) == 0:
                    logger.info(f"🛑 Empty properties list on page {page}")
                    break
                
                all_properties.extend(properties)
                logger.info(f"✅ Added {len(properties)} properties (total: {len(all_properties)})")
                
                # IMPROVED PAGINATION LOGIC
                # Method 1: Check explicit pagination flags
                has_next = False
                total_pages = None
                
                if isinstance(data, dict):
                    # Check has_next flags (explicit True/False)
                    if 'has_next' in data:
                        has_next = bool(data['has_next'])
                    elif 'hasNext' in data:
                        has_next = bool(data['hasNext'])
                    elif 'next' in data:
                        has_next = data['next'] is not None and data['next'] != ''
                    
                    # Check total pages
                    total_pages = (
                        data.get('total_pages') or 
                        data.get('totalPages') or 
                        data.get('num_pages') or
                        data.get('pages')
                    )
                    
                    # Check current page vs total pages
                    current_page = data.get('current_page') or data.get('page') or page
                    if total_pages and current_page >= total_pages:
                        logger.info(f"🏁 Reached last page {current_page}/{total_pages}")
                        break
                
                # Method 2: If no pagination info, check if we got a full page
                # Assume page size is 20 (adjust if your API uses different size)
                expected_page_size = 20
                if not has_next and total_pages is None:
                    # If we got fewer items than expected, it's probably the last page
                    if len(properties) < expected_page_size:
                        logger.info(f"🏁 Got only {len(properties)} items (less than {expected_page_size}), assuming last page")
                        break
                    # Otherwise continue to next page
                    logger.info(f"ℹ️ No pagination info but got full page, trying next page")
                elif has_next is False and total_pages is None:
                    logger.info(f"🏁 has_next is False, stopping")
                    break
                
                page += 1
                
            except Exception as e:
                logger.exception(f"❌ Error fetching page {page}: {e}")
                break
        
        logger.info(f"🏁 Total properties collected: {len(all_properties)}")
        
        if all_properties:
            # Log sample for debugging
            sample = all_properties[0]
            logger.info(f"📝 Sample property keys: {list(sample.keys()) if isinstance(sample, dict) else 'Not a dict'}")
            cache.set(cache_key, all_properties, 3600)
        else:
            logger.warning("⚠️ No properties collected!")
        
        return all_properties
    
    def location(self, obj):
        """
        Builds the URL for each property.
        """
        if not isinstance(obj, dict):
            logger.warning(f"⚠️ Property is not a dict: {type(obj)}")
            return None
        
        # Try slug first, then IDs
        slug = (
            obj.get('slug') or
            obj.get('seo_url') or
            obj.get('url_slug')
        )
        
        if slug:
            return f"/properties/{slug}/"
        
        # Fallback to ID
        prop_id = (
            obj.get('id') or
            obj.get('property_id') or
            obj.get('propertyId') or
            obj.get('pk')
        )
        
        if prop_id:
            return f"/properties/{prop_id}/"
        
        logger.warning(f"⚠️ Property missing slug/id. Keys: {list(obj.keys())}")
        return None
    
    def lastmod(self, obj):
        if not isinstance(obj, dict):
            return None
        
        return (
            obj.get('updated_at') or
            obj.get('modified_at') or
            obj.get('modified') or
            obj.get('updated') or
            obj.get('updatedAt') or
            obj.get('last_updated')
        )