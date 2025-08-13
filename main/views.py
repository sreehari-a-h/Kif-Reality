from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from urllib.parse import urlparse, parse_qs
import json

import requests

from .models import ContactMessage, Newsletter
from .services import PropertyService

API_BASE = "https://offplan.market/api/property"

def index(request):
    """Homepage with featured properties"""
    # Get featured properties
    properties_result = PropertyService.get_featured_properties()
    
    context = {
        'featured_properties': properties_result.get('data', {}).get('results', []) if properties_result['success'] else [],
        'properties_error': properties_result.get('error'),
    }
    return render(request, 'index.html', context)

def extract_page_number(url):
    if not url:
        return None
    try:
        from urllib.parse import urlparse, parse_qs
        query = urlparse(url).query
        page = parse_qs(query).get('page', [None])[0]
        return page
    except Exception as e:
        print(f"Pagination extraction error: {e}")
        return None


@csrf_exempt
def properties(request):
    filters = {}

    if request.method == 'POST':
        filters['property_type'] = request.POST.get('property_type')
        filters['city'] = request.POST.get('city')
        filters['min_price'] = request.POST.get('min_price')
        filters['max_price'] = request.POST.get('max_price')
        filters['page'] = request.POST.get('page')
    else:
        filters['page'] = request.GET.get('page')

    filters = {k: v for k, v in filters.items() if v}

    properties_result = PropertyService.get_properties(filters)
    
    mapped_properties = []
    if properties_result['success'] and properties_result['data'].get('status') is True:
        data_block = properties_result['data']['data']  # ✅ THIS is where the real results are
        for prop in data_block.get('results', []):
            title_data = prop.get('title', {})
            title = title_data.get('en', 'Untitled') if isinstance(title_data, dict) else (title_data or 'Untitled')

            city_data = prop.get('city', {})
            city_name = ''
            if isinstance(city_data, dict):
                name_data = city_data.get('name', {})
                city_name = name_data.get('en', '') if isinstance(name_data, dict) else name_data

            district_data = prop.get('district', {})
            district_name = ''
            if isinstance(district_data, dict):
                name_data = district_data.get('name', {})
                district_name = name_data.get('en', '') if isinstance(name_data, dict) else name_data

            mapped_properties.append({
                'id': prop.get('id'),
                'title': title,
                'image': prop.get('cover'),
                'location': f"{city_name}, {district_name}",
                'price': prop.get('low_price'),
                'area': prop.get('min_area'),
                'bedrooms': prop.get('bedrooms'),
                'bathrooms': prop.get('bathrooms'),
                'description': 'Explore more about this project at the detail page.',
            })

            
        
        next_page_num = extract_page_number(data_block.get('next_page_url'))
        prev_page_num = extract_page_number(data_block.get('previous_page_url'))
        current_page = data_block.get('current_page')
        last_page = data_block.get('last_page', (data_block.get('count', 0) // 12) + 1)
        def get_page_range(current_page, last_page, max_display=5):
            page_range = []

            if last_page <= max_display + 1:
                return list(range(1, last_page + 1))

            start = max(1, current_page - 2)
            end = min(start + max_display - 1, last_page - 1)

            page_range = list(range(start, end + 1))

            if last_page not in page_range:
                page_range.append('...')  # Add ellipsis
                page_range.append(last_page)

            return page_range

        if next_page_num == '3':
            prev_page_num = '1'

        # print("➡️ NEXT PAGE:", next_page_num)
        # print("➡️ PREV PAGE:", prev_page_num)

        context = {
            'properties': mapped_properties,
            'filters': filters,
            'total_count': data_block.get('count', 0),
            'next_page': next_page_num,
            'prev_page': prev_page_num,
            'current_page': data_block.get('current_page'),
            'last_page': data_block.get('last_page', (data_block.get('count', 0) // 12) + 1),  # assuming 12 per page
            'page_range': get_page_range(current_page, last_page), 
            'properties_error': None,
        }
    else:
        context = {
            'properties': [],
            'filters': filters,
            'total_count': 0,
            'next_page': None,
            'prev_page': None,
            'properties_error': properties_result.get('error', 'Unable to load properties.'),
        }

    return render(request, 'properties.html', context)

def property_detail(request, pk):
    """
    Fetch property data from the API and render property_detail.html
    """
    url = f"{API_BASE}/{pk}"
    try:
        resp = requests.get(url, timeout=8)
    except requests.RequestException as e:
        return render(request, "property_detail.html", {"property_error": "Failed to retrieve property data."})

    if resp.status_code != 200:
        return render(request, "property_detail.html", {"property_error": "Property not found or API error."})
    data = resp.json()
    if not data.get("status"):
        return render(request, "property_detail.html", {"property_error": data.get("message") or "API returned error."})

    prop = data.get("data") or {}
    # normalize a few fields for template convenience
    # ensure lists exist
    prop.setdefault("property_images", [])
    prop.setdefault("facilities", [])
    prop.setdefault("grouped_apartments", [])
    prop.setdefault("payment_plans", [])
    prop.setdefault("property_units", [])

    return render(request, "property_detail.html", {"property": prop})


def unit_detail(request, property_id, unit_id):
    """
    Show unit details. We fetch the property and locate the unit by id in either grouped_apartments or property_units.
    """
    url = f"{API_BASE}/{property_id}"
    try:
        resp = requests.get(url, timeout=8)
    except requests.RequestException:
        raise Http404("Property data could not be retrieved.")
    if resp.status_code != 200:
        raise Http404("Property not found.")

    data = resp.json()
    prop = data.get("data") or {}
    units = prop.get("property_units", []) or []
    grouped = prop.get("grouped_apartments", []) or []

    # Try to find unit in grouped_apartments by id
    unit = None
    for u in grouped + units:
        # some ids might be strings or ints; normalize
        try:
            if int(u.get("id")) == int(unit_id):
                unit = u
                break
        except Exception:
            if str(u.get("id")) == str(unit_id):
                unit = u
                break

    if not unit:
        raise Http404("Unit not found.")

    # supply property + unit to template
    context = {
        "property": prop,
        "unit": unit,
    }
    return render(request, "unit_detail.html", context)

def about(request):
    """About us page"""
    return render(request, 'about.html')

def blogs(request):
    """About us page"""
    return render(request, 'blogs.html')

def contact(request):
    """Contact us page"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        
        # Create contact message
        contact_message = ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message_text
        )
        
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('contact')
    
    return render(request, 'contact.html')

@csrf_exempt
@require_http_methods(["POST"])
def subscribe_newsletter(request):
    """Subscribe to newsletter"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'success': False, 'error': 'Email is required'})
        
        newsletter, created = Newsletter.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        
        if created:
            return JsonResponse({'success': True, 'message': 'Successfully subscribed to newsletter!'})
        else:
            return JsonResponse({'success': False, 'error': 'Email already subscribed'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'An error occurred'})

@require_http_methods(["GET"])
def search_properties_api(request):
    """API endpoint for property search"""
    query = request.GET.get('q', '')
    filters = {
        'search': query
    }
    
    result = PropertyService.search_properties(query, filters)
    
    if result['success']:
        return JsonResponse({
            'success': True,
            'properties': result['data'].get('results', []),
            'total': result['data'].get('count', 0)
        })
    else:
        return JsonResponse({
            'success': False,
            'error': result['error']
        })