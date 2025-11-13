# # main/sitemaps.py
# from django.contrib.sitemaps import Sitemap
# from django.urls import reverse
# from .services import PropertyService
# from django.core.cache import cache
# import logging
# import time

# logger = logging.getLogger(__name__)

# class PropertySitemap(Sitemap):
#     changefreq = "daily"
#     priority = 0.9
#     limit = 5000  # Max URLs per sitemap (Google limit is 50,000)
    
#     def items(self):
#         """
#         Fetch ALL 1600+ properties from the external API with proper pagination
#         """
#         # Check cache first (cache for 12 hours since you have 1600+ properties)
#         cache_key = 'sitemap_all_properties_v2'
#         cached_properties = cache.get(cache_key)
#         if cached_properties:
#             logger.info(f"[SITEMAP] ✅ Using cached properties: {len(cached_properties)} items")
#             print(f"🔄 [SITEMAP] Using cached properties: {len(cached_properties)} items")
#             return cached_properties
        
#         all_properties = []
#         page = 1
#         max_pages = 200  # With ~12 items per page, 200 pages = 2400 properties (buffer)
#         consecutive_empty_pages = 0
#         max_empty_pages = 3  # Stop after 3 consecutive empty pages
        
#         start_time = time.time()
        
#         try:
#             print(f"\n🚀 [SITEMAP] Starting to fetch ALL properties (expecting ~1600+)...")
#             logger.info("[SITEMAP] Starting sitemap generation for ~1600 properties")
            
#             while page <= max_pages:
#                 try:
#                     print(f"\n📄 [SITEMAP] Fetching page {page}...", end=" ")
                    
#                     # Fetch properties for current page
#                     result = PropertyService.get_properties(filters={'page': page})
                    
#                     # Check if API call was successful
#                     if not result.get('success'):
#                         error_msg = result.get('error', 'Unknown error')
#                         print(f"❌ Failed: {error_msg}")
#                         logger.warning(f"[SITEMAP] API failed on page {page}: {error_msg}")
#                         consecutive_empty_pages += 1
#                         if consecutive_empty_pages >= max_empty_pages:
#                             break
#                         page += 1
#                         continue
                    
#                     # Check nested status
#                     api_data = result.get('data', {})
#                     if not api_data.get('status'):
#                         print(f"⚠️  API status False")
#                         logger.warning(f"[SITEMAP] API status False on page {page}")
#                         consecutive_empty_pages += 1
#                         if consecutive_empty_pages >= max_empty_pages:
#                             break
#                         page += 1
#                         continue
                    
#                     # Get the data block: result['data']['data']['results']
#                     data_block = api_data.get('data', {})
#                     properties = data_block.get('results', [])
                    
#                     if not properties or len(properties) == 0:
#                         print(f"⚠️  Empty page")
#                         logger.info(f"[SITEMAP] Empty page {page}")
#                         consecutive_empty_pages += 1
#                         if consecutive_empty_pages >= max_empty_pages:
#                             print(f"\n🛑 [SITEMAP] Stopping: {max_empty_pages} consecutive empty pages")
#                             break
#                         page += 1
#                         continue
                    
#                     # Reset empty page counter
#                     consecutive_empty_pages = 0
                    
#                     # Filter valid properties
#                     valid_properties = []
#                     for prop in properties:
#                         if isinstance(prop, dict) and prop.get('id'):
#                             valid_properties.append(prop)
                    
#                     all_properties.extend(valid_properties)
                    
#                     # Get pagination info
#                     current_page = data_block.get('current_page', page)
#                     last_page = data_block.get('last_page')
#                     total_count = data_block.get('count', 'unknown')
#                     next_page_url = data_block.get('next_page_url')
                    
#                     print(f"✅ {len(valid_properties)} props | Total: {len(all_properties)}/{total_count}")
                    
#                     # Log every 10 pages
#                     if page % 10 == 0:
#                         elapsed = time.time() - start_time
#                         logger.info(f"[SITEMAP] Progress: Page {page}, Total properties: {len(all_properties)}, Time: {elapsed:.1f}s")
                    
#                     # Check if we've reached the last page
#                     if last_page and current_page >= last_page:
#                         print(f"\n🏁 [SITEMAP] Reached last page ({last_page})")
#                         logger.info(f"[SITEMAP] Reached last page {last_page}")
#                         break
                    
#                     # Check if there's no next page
#                     if not next_page_url:
#                         print(f"\n🏁 [SITEMAP] No next_page_url")
#                         logger.info(f"[SITEMAP] No next_page_url at page {page}")
#                         break
                    
#                     page += 1
                    
#                 except Exception as page_error:
#                     print(f"❌ Error on page {page}: {str(page_error)}")
#                     logger.error(f"[SITEMAP] Error on page {page}: {str(page_error)}")
#                     consecutive_empty_pages += 1
#                     if consecutive_empty_pages >= max_empty_pages:
#                         break
#                     page += 1
#                     continue
            
#             elapsed_time = time.time() - start_time
#             print(f"\n🎉 [SITEMAP] Complete! {len(all_properties)} properties in {elapsed_time:.1f}s")
#             logger.info(f"[SITEMAP] Generation complete: {len(all_properties)} properties in {elapsed_time:.1f}s")
            
#             # Cache for 12 hours (since you have many properties, longer cache is better)
#             if all_properties:
#                 cache.set(cache_key, all_properties, 60 * 60 * 12)
#                 print(f"💾 [SITEMAP] Cached {len(all_properties)} properties for 12 hours")
#                 logger.info(f"[SITEMAP] Cached {len(all_properties)} properties")
#             else:
#                 print(f"⚠️  [SITEMAP] WARNING: No properties fetched!")
#                 logger.warning("[SITEMAP] No properties fetched!")
            
#             return all_properties
            
#         except Exception as e:
#             import traceback
#             error_trace = traceback.format_exc()
#             print(f"\n❌ [SITEMAP] FATAL ERROR: {str(e)}")
#             print(f"Stack trace:\n{error_trace}")
#             logger.error(f"[SITEMAP] Fatal error: {str(e)}\n{error_trace}")
            
#             # Return what we have
#             if all_properties:
#                 print(f"⚠️  [SITEMAP] Returning partial results: {len(all_properties)} properties")
#             return all_properties
    
#     def location(self, obj):
#         """
#         Return the URL for each property
#         """
#         if not isinstance(obj, dict):
#             return None
        
#         property_id = obj.get('id')
#         if property_id:
#             try:
#                 return reverse('property_detail', kwargs={'pk': int(property_id)})
#             except (ValueError, TypeError):
#                 return None
#         return None
    
#     def lastmod(self, obj):
#         """
#         Return last modified date if available
#         """
#         if not isinstance(obj, dict):
#             return None
            
#         from datetime import datetime
        
#         date_field = obj.get('updated_at') or obj.get('modified_at')
        
#         if date_field:
#             try:
#                 if isinstance(date_field, str):
#                     return datetime.fromisoformat(date_field.replace('Z', '+00:00'))
#                 return date_field
#             except Exception:
#                 pass
        
#         return None