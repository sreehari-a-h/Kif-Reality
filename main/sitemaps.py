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
                
                # Check if API call was successful
                if not result['success']:
                    logger.warning(f"Failed to fetch properties page {page}: {result.get('error')}")
                    break
                
                # Check if the nested status is True
                if not result['data'].get('status'):
                    logger.warning(f"API returned status False on page {page}")
                    break
                
                # Navigate to the actual data: result['data']['data']['results']
                data_block = result['data'].get('data', {})
                properties = data_block.get('results', [])
                
                if not properties:
                    logger.info(f"No more properties found on page {page}")
                    break
                
                # Filter out non-dict items (safety check)
                valid_properties = [prop for prop in properties if isinstance(prop, dict)]
                
                if not valid_properties:
                    break
                
                all_properties.extend(valid_properties)
                logger.info(f"Fetched {len(valid_properties)} properties from page {page}")
                
                # Check if there's a next page
                next_page_url = data_block.get('next_page_url')
                current_page = data_block.get('current_page', page)
                last_page = data_block.get('last_page', 1)
                
                if not next_page_url or current_page >= last_page:
                    logger.info(f"Reached last page: {current_page}")
                    break
                
                page += 1
            
            logger.info(f"Total properties in sitemap: {len(all_properties)}")
            return all_properties
            
        except Exception as e:
            logger.error(f"Error fetching properties for sitemap: {str(e)}", exc_info=True)
            return []
    
    def location(self, obj):
        """
        Return the URL for each property using 'pk' or 'id'
        """
        # Safety check
        if not isinstance(obj, dict):
            logger.error(f"Expected dict but got {type(obj)}: {obj}")
            return None
        
        # Get property ID
        property_id = obj.get('id')
        
        if property_id:
            try:
                return reverse('property_detail', kwargs={'pk': int(property_id)})
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid property ID: {property_id} - {e}")
                return None
        
        logger.warning(f"Property missing ID field. Available keys: {list(obj.keys())}")
        return None
    
    def lastmod(self, obj):
        """
        Return last modified date if available in API response
        """
        if not isinstance(obj, dict):
            return None
            
        from datetime import datetime
        
        # Try different common field names
        date_field = obj.get('updated_at') or obj.get('modified_at') or obj.get('last_modified')
        
        if date_field:
            try:
                # Handle ISO format dates
                if isinstance(date_field, str):
                    # Remove 'Z' and add timezone info
                    date_str = date_field.replace('Z', '+00:00')
                    return datetime.fromisoformat(date_str)
                return date_field
            except Exception as e:
                logger.warning(f"Could not parse date {date_field}: {e}")
        
        return None