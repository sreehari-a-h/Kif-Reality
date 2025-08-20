from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from urllib.parse import urlparse, parse_qs
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .models import Contact
import json

import requests

from .services import PropertyService

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from .models import BlogPost, Category, Tag, Newsletter, Comment
from .forms import NewsletterForm, CommentForm


def blog_list(request):
    """Display blog list page with pagination and filtering"""
    posts = BlogPost.objects.filter(status='published').select_related(
        'category', 'author'
    ).prefetch_related('tags')
    
    # Get featured post
    featured_post = posts.filter(is_featured=True).first()
    
    # Filter by category if specified
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Filter by tag if specified
    tag_slug = request.GET.get('tag')
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    # Pagination
    paginator = Paginator(posts, 6)  # Show 6 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Sidebar data
    categories = Category.objects.annotate(
        posts_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(posts_count__gt=0)
    
    recent_posts = BlogPost.objects.filter(status='published').order_by('-published_at')[:3]
    popular_tags = Tag.objects.annotate(
        posts_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(posts_count__gt=0).order_by('-posts_count')[:10]
    
    context = {
        'featured_post': featured_post,
        'page_obj': page_obj,
        'categories': categories,
        'recent_posts': recent_posts,
        'popular_tags': popular_tags,
        'search_query': search_query,
        'newsletter_form': NewsletterForm(),
    }
    
    return render(request, 'blogs.html', context)


def blog_detail(request, slug):
    """Display individual blog post with comment functionality"""
    post = get_object_or_404(
        BlogPost.objects.select_related('category', 'author').prefetch_related('tags'),
        slug=slug,
        status='published'
    )
    
    # Increment view count
    post.increment_views()
    
    # Get approved comments
    comments = post.comments.filter(is_approved=True).order_by('-created_at')
    
    # Related posts
    related_posts = BlogPost.objects.filter(
        category=post.category,
        status='published'
    ).exclude(id=post.id)[:3]
    
    # Initialize comment form
    comment_form = CommentForm()
    comment_success = False
    
    # Handle comment form submission
    if request.method == 'POST':
        # Check if it's a comment submission
        if 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                try:
                    # Create comment but don't save to database yet
                    comment = comment_form.save(commit=False)
                    # Associate comment with the current post
                    comment.post = post
                    # Save to database
                    comment.save()
                    
                    # Set success flag
                    comment_success = True
                    
                    # Add success message
                    messages.success(
                        request, 
                        'Thank you for your comment! It has been submitted and is awaiting approval.'
                    )
                    
                    # Reset form after successful submission
                    comment_form = CommentForm()
                    
                    # Redirect to prevent re-submission on refresh
                    return redirect('blog_detail', slug=slug)
                    
                except Exception as e:
                    print(f"Error saving comment: {e}")  # For debugging
                    messages.error(
                        request, 
                        'Sorry, there was an error submitting your comment. Please try again.'
                    )
            else:
                # Form has validation errors
                messages.error(
                    request, 
                    'Please correct the errors in your comment form.'
                )
    
    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
        'comment_form': comment_form,
        'comment_success': comment_success,
    }
    
    return render(request, 'blog_detail.html', context)


def blog_category(request, slug):
    """Display posts by category"""
    category = get_object_or_404(Category, slug=slug)
    posts = BlogPost.objects.filter(
        category=category,
        status='published'
    ).select_related('author').prefetch_related('tags')
    
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'categories': Category.objects.annotate(
            posts_count=Count('posts', filter=Q(posts__status='published'))
        ).filter(posts_count__gt=0),
    }
    
    return render(request, 'blog_category.html', context)


def blog_tag(request, slug):
    """Display posts by tag"""
    tag = get_object_or_404(Tag, slug=slug)
    posts = BlogPost.objects.filter(
        tags=tag,
        status='published'
    ).select_related('category', 'author').prefetch_related('tags')
    
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'page_obj': page_obj,
        'popular_tags': Tag.objects.annotate(
            posts_count=Count('posts', filter=Q(posts__status='published'))
        ).filter(posts_count__gt=0).order_by('-posts_count')[:10],
    }
    
    return render(request, 'blog_tag.html', context)

@require_POST
def newsletter_subscribe(request):
    """Handle newsletter subscription via AJAX"""
    try:
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            newsletter, created = Newsletter.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )
            
            if created:
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for subscribing to our newsletter!'
                })
            elif not newsletter.is_active:
                newsletter.is_active = True
                newsletter.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Your subscription has been reactivated!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'You are already subscribed to our newsletter.'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please enter a valid email address.'
            })
    except Exception as e:
        print(f"Newsletter subscription error: {e}")  # For debugging
        return JsonResponse({
            'success': False,
            'message': 'Sorry, there was an error processing your subscription. Please try again.'
        })


def blog_search(request):
    """Handle blog search functionality"""
    query = request.GET.get('q', '').strip()
    posts = BlogPost.objects.none()
    
    if query:
        posts = BlogPost.objects.filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(category__name__icontains=query),
            status='published'
        ).distinct().select_related('category', 'author').prefetch_related('tags')
    
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': query,
        'results_count': posts.count(),
        'categories': Category.objects.annotate(
            posts_count=Count('posts', filter=Q(posts__status='published'))
        ).filter(posts_count__gt=0),
        'popular_tags': Tag.objects.annotate(
            posts_count=Count('posts', filter=Q(posts__status='published'))
        ).filter(posts_count__gt=0).order_by('-posts_count')[:10],
    }
    
    return render(request, 'blog_search.html', context)

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

def exclusive(request):
    """Homepage with featured properties"""
    # Get featured properties
    # properties_result = PropertyService.get_featured_properties()
    
    # context = {
    #     'featured_properties': properties_result.get('data', {}).get('results', []) if properties_result['success'] else [],
    #     'properties_error': properties_result.get('error'),
    # }
    return render(request, 'properties/exclusive_list.html')

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

def model(request):
    """Model page"""
    return render(request, 'model.html')

def model1(request):
    """Model 1 page"""
    return render(request, 'model1.html')

def model2(request):
    """Model 2 page"""
    return render(request, 'model2.html')

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

def contact_view(request):
    """Display the contact page"""
    return render(request, 'contact.html')

@require_http_methods(["POST"])
def contact_submit(request):
    """Handle contact form submission"""
    try:
        # Get form data
        first_name = request.POST.get('firstName', '').strip()
        last_name = request.POST.get('lastName', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        # Validate required fields
        if not all([first_name, last_name, email, phone]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('contact')
        
        # Get optional fields
        investment_budget = request.POST.get('investmentBudget', '')
        investment_type = request.POST.get('investmentType', '')
        preferred_location = request.POST.get('preferredLocation', '')
        timeline = request.POST.get('timeline', '')
        message = request.POST.get('message', '')
        
        # Handle property interests (multiple checkboxes)
        property_interests = request.POST.getlist('propertyInterest')
        
        # Create contact record
        contact = Contact.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            investment_budget=investment_budget,
            investment_type=investment_type,
            preferred_location=preferred_location,
            timeline=timeline,
            message=message,
            property_interests=', '.join(property_interests) if property_interests else ''
        )
        
        # Send notification email (optional)
        try:
            send_notification_email(contact)
        except Exception as e:
            # Log the error but don't fail the form submission
            print(f"Email notification failed: {e}")
        
        messages.success(request, 'Thank you for your inquiry! Our team will contact you within 24 hours.')
        return redirect('contact')
        
    except Exception as e:
        print(f"Contact form error: {e}")
        messages.error(request, 'An error occurred while submitting your inquiry. Please try again.')
        return redirect('contact')

@csrf_exempt
@require_http_methods(["POST"])
def contact_submit_ajax(request):
    """Handle AJAX contact form submission"""
    try:
        # Parse JSON data for AJAX requests
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        # Get form data
        first_name = data.get('firstName', '').strip()
        last_name = data.get('lastName', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        
        # Validate required fields
        if not all([first_name, last_name, email, phone]):
            return JsonResponse({
                'success': False,
                'message': 'Please fill in all required fields.'
            }, status=400)
        
        # Get optional fields
        investment_budget = data.get('investmentBudget', '')
        investment_type = data.get('investmentType', '')
        preferred_location = data.get('preferredLocation', '')
        timeline = data.get('timeline', '')
        message = data.get('message', '')
        
        # Handle property interests
        if isinstance(data.get('propertyInterest'), list):
            property_interests = data.get('propertyInterest', [])
        else:
            property_interests = data.getlist('propertyInterest') if hasattr(data, 'getlist') else []
        
        # Create contact record
        contact = Contact.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            investment_budget=investment_budget,
            investment_type=investment_type,
            preferred_location=preferred_location,
            timeline=timeline,
            message=message,
            property_interests=', '.join(property_interests) if property_interests else ''
        )
        
        # Send notification email (optional)
        try:
            send_notification_email(contact)
        except Exception as e:
            print(f"Email notification failed: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you for your inquiry! Our team will contact you within 24 hours.',
            'contact_id': contact.id
        })
        
    except Exception as e:
        print(f"AJAX Contact form error: {e}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while submitting your inquiry. Please try again.'
        }, status=500)

def send_notification_email(contact):
    """Send notification email to admin and confirmation to user"""
    
    # Admin notification email
    admin_subject = f"New Contact Inquiry from {contact.full_name}"
    admin_message = f"""
    New contact inquiry received:
    
    Name: {contact.full_name}
    Email: {contact.email}
    Phone: {contact.phone}
    
    Investment Details:
    Budget: {contact.get_investment_budget_display() if contact.investment_budget else 'Not specified'}
    Type: {contact.get_investment_type_display() if contact.investment_type else 'Not specified'}
    Location: {contact.get_preferred_location_display() if contact.preferred_location else 'Not specified'}
    Timeline: {contact.get_timeline_display() if contact.timeline else 'Not specified'}
    
    Property Interests: {contact.property_interests or 'None specified'}
    
    Message: {contact.message or 'No additional message'}
    
    Submitted: {contact.created_at.strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    # Send to admin
    if hasattr(settings, 'ADMIN_EMAIL'):
        send_mail(
            admin_subject,
            admin_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True,
        )
    
    # User confirmation email
    user_subject = "Thank you for contacting KIF Realty"
    user_message = f"""
    Dear {contact.first_name},
    
    Thank you for your interest in Dubai real estate investment. We have received your inquiry and our RERA-certified experts will contact you within 24 hours.
    
    Your Inquiry Details:
    - Investment Budget: {contact.get_investment_budget_display() if contact.investment_budget else 'Not specified'}
    - Investment Type: {contact.get_investment_type_display() if contact.investment_type else 'Not specified'}
    - Preferred Location: {contact.get_preferred_location_display() if contact.preferred_location else 'Not specified'}
    - Timeline: {contact.get_timeline_display() if contact.timeline else 'Not specified'}
    
    In the meantime, feel free to reach out directly:
    📞 +971 50 964 7864
    📧 info@kifrealty.ae
    💬 WhatsApp: https://wa.me/971509647864
    
    Best regards,
    KIF Realty Team
    """
    
    send_mail(
        user_subject,
        user_message,
        settings.DEFAULT_FROM_EMAIL,
        [contact.email],
        fail_silently=True,
    )

@require_POST
@csrf_exempt  # Remove this in production and handle CSRF properly
def submit_comment_ajax(request, slug):
    """Handle comment submission via AJAX"""
    try:
        post = get_object_or_404(BlogPost, slug=slug, status='published')
        
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your comment! It has been submitted and is awaiting approval.',
                'comment_count': post.comments.filter(is_approved=True).count()
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors in your form.',
                'errors': form.errors
            })
    except Exception as e:
        print(f"Comment submission error: {e}")  # For debugging
        return JsonResponse({
            'success': False,
            'message': 'Sorry, there was an error submitting your comment. Please try again.'
        })
