# main/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .services import PropertyService
import logging

logger = logging.getLogger(__name__)

class PropertySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    
    def items(self):
        """
        Fetch all properties from the external API with pagination
        """
        all_properties = []
        page = 1
        max_pages = 100  # Safety limit to prevent infinite loops
        
        try:
            while page <= max_pages:
                result = PropertyService.get_properties(filters={'page': page})
                
                if not result['success'] or not result['data']:
                    logger.warning(f"Failed to fetch properties page {page}")
                    break
                
                # Adjust based on your API response structure
                # Common structures: {'results': [...], 'next': '...', 'count': ...}
                data = result['data']
                
                # Try to get properties from different possible structures
                if isinstance(data, list):
                    properties = data
                elif 'results' in data:
                    properties = data['results']
                elif 'data' in data:
                    properties = data['data']
                else:
                    properties = []
                
                if not properties:
                    break
                
                all_properties.extend(properties)
                logger.info(f"Fetched {len(properties)} properties from page {page}")
                
                # Check if there are more pages
                has_next = data.get('next') or (page < data.get('total_pages', page))
                if not has_next:
                    break
                
                page += 1
            
            logger.info(f"Total properties in sitemap: {len(all_properties)}")
            return all_properties
            
        except Exception as e:
            logger.error(f"Error fetching properties for sitemap: {e}")
            return []
    
    def location(self, obj):
        """
        Return the URL for each property using 'pk' or 'id'
        """
        # Try 'id' first, then 'pk', then 'property_id'
        property_id = obj.get('id') or obj.get('pk') or obj.get('property_id')
        
        if property_id:
            return reverse('property_detail', kwargs={'pk': property_id})
        
        logger.warning(f"Property missing ID field: {obj}")
        return None
    
    def lastmod(self, obj):
        """
        Return last modified date if available in API response
        """
        from datetime import datetime
        
        # Try different common field names
        date_field = obj.get('updated_at') or obj.get('modified_at') or obj.get('last_modified')
        
        if date_field:
            try:
                # Handle ISO format dates
                if isinstance(date_field, str):
                    return datetime.fromisoformat(date_field.replace('Z', '+00:00'))
                return date_field
            except Exception as e:
                logger.warning(f"Could not parse date {date_field}: {e}")
        
        return None