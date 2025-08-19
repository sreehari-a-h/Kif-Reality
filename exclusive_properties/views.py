from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from .models import ExclusiveProperty, PropertyInquiry
import json

def exclusive_properties_list(request):
    """List view for exclusive properties with filtering"""
    properties = ExclusiveProperty.objects.filter(
        is_exclusive=True,
        status__in=['available', 'under_offer']
    ).select_related('assigned_agent').prefetch_related('images', 'amenities')
    
    # Apply filters
    property_type = request.GET.get('property_type')
    location = request.GET.get('location')
    bedrooms = request.GET.get('bedrooms')
    budget = request.GET.get('budget')
    
    if property_type:
        properties = properties.filter(property_type=property_type)
    
    if location:
        properties = properties.filter(
            Q(district__icontains=location) |
            Q(neighborhood__icontains=location) |
            Q(city__icontains=location)
        )
    
    if bedrooms:
        if bedrooms == 'studio':
            properties = properties.filter(bedrooms=0)
        elif bedrooms.isdigit():
            bedroom_count = int(bedrooms)
            if bedroom_count == 4:
                properties = properties.filter(bedrooms__gte=4)
            else:
                properties = properties.filter(bedrooms=bedroom_count)
    
    if budget:
        if budget.endswith('+'):
            min_price = int(budget.replace('+', ''))
            properties = properties.filter(price__gte=min_price)
        elif '-' in budget:
            min_price, max_price = map(int, budget.split('-'))
            properties = properties.filter(price__gte=min_price, price__lte=max_price)
    
    # Pagination
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options for the form
    property_types = ExclusiveProperty.PROPERTY_TYPES
    locations = ExclusiveProperty.objects.values_list('district', flat=True).distinct()
    
    context = {
        'properties': page_obj,
        'property_types': property_types,
        'locations': locations,
        'total_count': properties.count(),
        'filters': {
            'property_type': property_type,
            'location': location,
            'bedrooms': bedrooms,
            'budget': budget,
        }
    }
    
    return render(request, 'properties/exclusive_list.html', context)


def exclusive_property_detail(request, slug):
    """Detail view for individual exclusive property"""
    property_obj = get_object_or_404(
        ExclusiveProperty,
        slug=slug,
        is_exclusive=True
    )
    
    # Increment view count
    property_obj.view_count += 1
    property_obj.save(update_fields=['view_count'])
    
    # Get related properties
    related_properties = ExclusiveProperty.objects.filter(
        is_exclusive=True,
        status__in=['available', 'under_offer'],
        district=property_obj.district
    ).exclude(id=property_obj.id)[:3]
    
    context = {
        'property': property_obj,
        'related_properties': related_properties,
        'images': property_obj.images.all(),
        'amenities': property_obj.amenities.all(),
    }
    
    return render(request, 'properties/exclusive_detail.html', context)


@require_POST
@csrf_exempt
def submit_property_inquiry(request):
    """Handle property inquiry form submissions"""
    try:
        data = json.loads(request.body)
        
        property_id = data.get('property_id')
        property_obj = get_object_or_404(ExclusiveProperty, id=property_id)
        
        inquiry = PropertyInquiry.objects.create(
            property=property_obj,
            inquiry_type=data.get('inquiry_type', 'info'),
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone', ''),
            message=data.get('message', ''),
            preferred_contact_method=data.get('contact_method', 'email'),
            budget_min=data.get('budget_min'),
            budget_max=data.get('budget_max'),
        )
        
        # Increment inquiry count
        property_obj.inquiry_count += 1
        property_obj.save(update_fields=['inquiry_count'])
        
        # Send notification email (implement as needed)
        # send_inquiry_notification.delay(inquiry.id)
        
        return JsonResponse({
            'success': True,
            'message': 'Your inquiry has been submitted successfully. We will contact you soon.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }, status=400)


def exclusive_properties_api(request):
    """API endpoint for exclusive properties (for AJAX calls)"""
    properties = ExclusiveProperty.objects.filter(
        is_exclusive=True,
        status__in=['available', 'under_offer']
    ).values(
        'id', 'title', 'slug', 'property_type', 'district',
        'bedrooms', 'bathrooms', 'area_sqft', 'price',
        'cover_image', 'short_description'
    )
    
    return JsonResponse(list(properties), safe=False)
