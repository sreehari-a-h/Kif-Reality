from django.contrib.sitemaps import Sitemap
from django.core.cache import cache
from main.services import PropertyService
import logging

logger = logging.getLogger(__name__)

class PropertySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    limit = 5000  # Django splits sitemap into multiple files if needed

    def items(self):
        """
        Fetch all properties from the API with pagination.
        Returns a list of property dictionaries.
        """
        cache_key = 'property_sitemap_items'
        cached_items = cache.get(cache_key)
        if cached_items:
            logger.info(f"Using cached sitemap items: {len(cached_items)} properties")
            return cached_items

        all_properties = []
        page = 1
        max_pages = 100  # Safety limit to avoid infinite loops

        while page <= max_pages:
            try:
                logger.info(f"Fetching property page {page}")
                result = PropertyService.get_properties({'page': page})

                if not result or not result.get('success'):
                    logger.warning(f"API failed on page {page}: {result.get('error') if result else 'No response'}")
                    break

                data = result.get('data')
                if not data:
                    logger.warning(f"No data returned on page {page}")
                    break

                # Extract properties list - try common keys
                properties = None
                if isinstance(data, dict):
                    for key in ['results', 'data', 'items', 'properties', 'property_list']:
                        if key in data:
                            properties = data[key]
                            break
                elif isinstance(data, list):
                    properties = data

                if not properties or not isinstance(properties, list) or len(properties) == 0:
                    logger.info(f"No more properties found on page {page}, stopping")
                    break

                all_properties.extend(properties)

                # Pagination logic
                total_pages = data.get('total_pages') or data.get('pages') or data.get('num_pages') or data.get('totalPages')
                has_next = data.get('has_next', False) or data.get('hasNext', False) or (data.get('next') is not None)

                if total_pages and page >= total_pages:
                    break
                if not has_next and total_pages is None:
                    break

                page += 1

            except Exception as e:
                logger.exception(f"Error fetching property page {page}: {e}")
                break

        logger.info(f"Total properties collected: {len(all_properties)}")

        if all_properties:
            cache.set(cache_key, all_properties, 3600)  # Cache for 1 hour

        return all_properties

    def location(self, obj):
        """
        Build the URL for each property.
        """
        if isinstance(obj, dict):
            prop_id = (
                obj.get('id') or 
                obj.get('property_id') or 
                obj.get('pk') or
                obj.get('_id') or
                obj.get('propertyId')
            )
            if prop_id:
                return f"/property/{prop_id}/"
            logger.warning(f"Property missing ID: {obj}")
            return None
        elif isinstance(obj, (str, int)):
            return f"/property/{obj}/"
        return None

    def lastmod(self, obj):
        """
        Return last modified date for the property.
        """
        if isinstance(obj, dict):
            return (
                obj.get('updated_at') or 
                obj.get('modified_at') or 
                obj.get('modified') or 
                obj.get('last_updated') or
                obj.get('updated') or
                obj.get('updatedAt')
            )
        return None
