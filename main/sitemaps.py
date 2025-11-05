from django.contrib.sitemaps import Sitemap
from django.core.cache import cache
from main.services import PropertyService
import logging

logger = logging.getLogger(__name__)

class PropertySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    limit = 5000  # Increase for better performance (Google allows up to 50k)
    
    def items(self):
        """
        Fetch all properties from the API with pagination.
        Returns a list of property dictionaries.
        """
        # Try to get cached results first (cache for 1 hour)
        cache_key = 'property_sitemap_items'
        cached_items = cache.get(cache_key)
        if cached_items:
            logger.info(f"Using cached sitemap items: {len(cached_items)} properties")
            return cached_items
        
        all_properties = []
        page = 1
        max_pages = 100  # Safety limit to prevent infinite loops
        
        while page <= max_pages:
            try:
                logger.info(f"Fetching property page {page}")
                result = PropertyService.get_properties({'page': page})
                
                # Check if API call succeeded
                if not result or not result.get('success'):
                    logger.warning(f"Property API failed or returned no success on page {page}")
                    break
                
                # Extract data from response
                data = result.get('data', result)
                if not isinstance(data, dict):
                    logger.warning(f"Unexpected data format on page {page}: {type(data)}")
                    break
                
                # Get properties list from various possible keys
                properties = (
                    data.get('results') or 
                    data.get('data') or 
                    data.get('items') or 
                    data.get('properties') or
                    []
                )
                
                if not properties:
                    logger.info(f"No properties found on page {page}, stopping pagination")
                    break
                
                # Validate that we got a list
                if not isinstance(properties, list):
                    logger.warning(f"Properties is not a list on page {page}: {type(properties)}")
                    break
                
                # Add properties to our collection
                all_properties.extend(properties)
                logger.debug(f"Added {len(properties)} properties from page {page}")
                
                # Check if there are more pages
                total_pages = data.get('total_pages') or data.get('pages')
                has_next = data.get('has_next', False)
                
                # Stop if we've reached the last page
                if total_pages and page >= total_pages:
                    logger.info(f"Reached last page {page} of {total_pages}")
                    break
                
                if not has_next and total_pages is None:
                    logger.info(f"No more pages after page {page}")
                    break
                
                page += 1
                
            except Exception as e:
                logger.exception(f"Error fetching property sitemap page {page}: {e}")
                break
        
        logger.info(f"Total properties collected for sitemap: {len(all_properties)}")
        
        # Cache the results for 1 hour
        if all_properties:
            cache.set(cache_key, all_properties, 3600)
        
        return all_properties
    
    def location(self, obj):
        """
        Build the URL for each property.
        Returns path like: /property/123/
        """
        if isinstance(obj, dict):
            prop_id = obj.get('id') or obj.get('property_id') or obj.get('pk')
            if prop_id:
                return f"/property/{prop_id}/"
            else:
                logger.warning(f"Property object missing ID: {obj}")
        elif isinstance(obj, (str, int)):
            return f"/property/{obj}/"
        
        return None  # Return None to exclude invalid items
    
    def lastmod(self, obj):
        """
        Return the last modified date for the property.
        Django will parse various datetime formats automatically.
        """
        if isinstance(obj, dict):
            # Try various common field names for updated timestamp
            timestamp = (
                obj.get('updated_at') or 
                obj.get('modified_at') or 
                obj.get('modified') or 
                obj.get('last_updated')
            )
            return timestamp
        return None