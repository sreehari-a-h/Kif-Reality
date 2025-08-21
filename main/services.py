import requests
import logging
from django.conf import settings
from typing import Dict, Optional

logger = logging.getLogger(__name__)

ALLOWED_FILTER_KEYS = {
    'city',
    'district',
    'property_type',
    'unit_type',
    'rooms',
    'delivery_year',
    'min_price',
    'max_price',
    'min_area',
    'max_area',
    'property_status',
    'sales_status',
    'title',
    'developer'
}

class PropertyService:
    @staticmethod
    def get_properties(filters: Optional[Dict] = None) -> Dict:
        """
        Fetch properties from external API using POST and valid JSON body.
        """
        # print("💡 [DEBUG] PropertyService.get_properties called with:", filters)

        try:
            raw_filters = filters or {}

            # Only send allowed filters
            payload = {
                key: value for key, value in raw_filters.items()
                if key in ALLOWED_FILTER_KEYS and value is not None and value != ''
            }
            logger.debug(f"Sending filters to API: {payload}")


            # Keep only page and featured from optional keys
            if 'page' in raw_filters:
                payload['page'] = raw_filters['page']
            if 'featured' in raw_filters:
                payload['featured'] = raw_filters['featured']

            # Separate 'page' from payload
            page = raw_filters.get('page')
            params = {'page': page} if page else {}

            response = requests.post(
                settings.PROPERTIES_API_URL,
                params=params,  # ⬅️ send page as query param
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=settings.API_TIMEOUT
            )


            response.raise_for_status()
            data = response.json()
            print("📤 Payload being sent to API:", payload)
            print("📤 Response being received:", data)


            return {
                'success': True,
                'data': data,
                'error': None
            }

        except requests.exceptions.Timeout:
            logger.error("API request timed out")
            return {
                'success': False,
                'data': None,
                'error': 'Request timed out. Please try again.'
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return {
                'success': False,
                'data': None,
                'error': 'Unable to fetch properties. Please try again later.'
            }

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'data': None,
                'error': 'An unexpected error occurred.'
            }

    @staticmethod
    def get_featured_properties() -> Dict:
        """
        Get featured properties for homepage.
        """
        filters = {
            # 'featured': True
        }
        return PropertyService.get_properties(filters)

    @staticmethod
    def search_properties(query: str, filters: Optional[Dict] = None) -> Dict:
        """
        Search properties with query and allowed filters.
        """
        search_filters = filters or {}
        search_filters['title'] = query
        return PropertyService.get_properties(search_filters)

    @staticmethod
    def get_cities() -> Dict:
        """
        Get cities with districts from external API.
        """
        try:
            response = requests.get(
                settings.CITIES_API_URL,
                timeout=settings.API_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'data': data,
                'error': None
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Cities API request failed: {str(e)}")
            return {
                'success': False,
                'data': [],
                'error': 'Unable to fetch cities data.'
            }
        except Exception as e:
            logger.error(f"Unexpected error fetching cities: {str(e)}")
            return {
                'success': False,
                'data': [],
                'error': 'An unexpected error occurred.'
            }

    @staticmethod
    def get_developers() -> Dict:
        """
        Get developers list from external API.
        """
        try:
            response = requests.get(
                settings.DEVELOPERS_API_URL,
                timeout=settings.API_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'data': data,
                'error': None
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Developers API request failed: {str(e)}")
            return {
                'success': False,
                'data': [],
                'error': 'Unable to fetch developers data.'
            }
        except Exception as e:
            logger.error(f"Unexpected error fetching developers: {str(e)}")
            return {
                'success': False,
                'data': [],
                'error': 'An unexpected error occurred.'
            }