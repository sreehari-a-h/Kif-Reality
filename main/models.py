## 4. main/models.py
from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.utils import timezone
from django import forms
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from PIL import Image
import os


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.TextField(max_length=300, help_text="Brief description shown in blog list")
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog_images/', help_text="Main image for the blog post")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False, help_text="Show as featured post on blog page")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    meta_keywords = models.CharField(max_length=200, blank=True, help_text="SEO keywords (comma separated)")
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['status']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
            
        super().save(*args, **kwargs)
        
        # Resize featured image if it's too large
        if self.featured_image:
            img_path = self.featured_image.path
            if os.path.exists(img_path):
                with Image.open(img_path) as img:
                    if img.height > 600 or img.width > 1200:
                        img.thumbnail((1200, 600), Image.Resampling.LANCZOS)
                        img.save(img_path, optimize=True, quality=85)
    
    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})
    
    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])
    
    @property
    def reading_time(self):
        """Calculate estimated reading time based on content length"""
        words = len(self.content.split())
        return max(1, round(words / 200))  # Average reading speed: 200 words per minute
    
    @property
    def comment_count(self):
        return self.comments.filter(is_approved=True).count()


class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    website = models.URLField(blank=True)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Comment by {self.name} on {self.post.title}'


class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email

# class ContactMessage(models.Model):
#     name = models.CharField(max_length=100)
#     email = models.EmailField(validators=[EmailValidator()])
#     phone = models.CharField(
#         max_length=15, 
#         validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')]
#     )
#     subject = models.CharField(max_length=200)
#     message = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_read = models.BooleanField(default=False)

#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"{self.name} - {self.subject}"

# class Newsletter(models.Model):
#     email = models.EmailField(unique=True, validators=[EmailValidator()])
#     subscribed_at = models.DateTimeField(auto_now_add=True)
#     is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return self.email

class Contact(models.Model):
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Investment Details
    BUDGET_CHOICES = [
        ('500k-1m', '500K - 1M AED'),
        ('1m-2m', '1M - 2M AED'),
        ('2m-5m', '2M - 5M AED'),
        ('5m-10m', '5M - 10M AED'),
        ('10m+', '10M+ AED'),
    ]
    investment_budget = models.CharField(max_length=20, choices=BUDGET_CHOICES, blank=True)
    
    INVESTMENT_TYPE_CHOICES = [
        ('buy-to-live', 'Buy to Live'),
        ('buy-to-rent', 'Buy to Rent'),
        ('off-plan', 'Off-Plan Investment'),
        ('commercial', 'Commercial Property'),
        ('portfolio', 'Property Portfolio'),
    ]
    investment_type = models.CharField(max_length=20, choices=INVESTMENT_TYPE_CHOICES, blank=True)
    
    # Property Interests (stored as comma-separated values)
    property_interests = models.TextField(blank=True, help_text="Comma-separated property interests")
    
    LOCATION_CHOICES = [
        ('downtown-dubai', 'Downtown Dubai'),
        ('dubai-marina', 'Dubai Marina'),
        ('palm-jumeirah', 'Palm Jumeirah'),
        ('dubai-hills', 'Dubai Hills Estate'),
        ('business-bay', 'Business Bay'),
        ('jvc', 'Jumeirah Village Circle'),
        ('dubai-south', 'Dubai South'),
        ('palm-jebel-ali', 'Palm Jebel Ali'),
        ('other', 'Other / Multiple'),
    ]
    preferred_location = models.CharField(max_length=30, choices=LOCATION_CHOICES, blank=True)
    
    TIMELINE_CHOICES = [
        ('immediate', 'Immediate (This Month)'),
        ('3-months', 'Next 3 Months'),
        ('6-months', 'Next 6 Months'),
        ('1-year', 'Within 1 Year'),
        ('exploring', 'Just Exploring'),
    ]
    timeline = models.CharField(max_length=20, choices=TIMELINE_CHOICES, blank=True)
    
    # Additional Information
    message = models.TextField(blank=True, help_text="Additional requirements or questions")
    
    # System Fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_contacted = models.BooleanField(default=False, help_text="Mark as contacted")
    
    class Meta:
        db_table = 'contact_inquiries'
        verbose_name = 'Contact Inquiry'
        verbose_name_plural = 'Contact Inquiries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def property_interests_list(self):
        """Return property interests as a list"""
        if self.property_interests:
            return [interest.strip() for interest in self.property_interests.split(',')]
        return []
    
    def set_property_interests(self, interests_list):
        """Set property interests from a list"""
        if interests_list:
            self.property_interests = ', '.join(interests_list)
        else:
            self.property_interests = ''

class ContactForm(forms.ModelForm):
    """Django ModelForm for Contact model (alternative to manual form handling)"""
    
    property_interests = forms.MultipleChoiceField(
        choices=[
            ('luxury-villa', 'Luxury Villas'),
            ('penthouse', 'Penthouses'),
            ('apartment', 'Apartments'),
            ('townhouse', 'Townhouses'),
            ('off-plan', 'Off-Plan Properties'),
            ('commercial', 'Commercial'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Property Interests"
    )
    
    class Meta:
        model = Contact
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'investment_budget', 'investment_type', 'preferred_location',
            'timeline', 'property_interests', 'message'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'investment_budget': forms.Select(attrs={'class': 'form-control'}),
            'investment_type': forms.Select(attrs={'class': 'form-control'}),
            'preferred_location': forms.Select(attrs={'class': 'form-control'}),
            'timeline': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Tell us more about your specific requirements, preferred amenities, or any questions you have about Dubai real estate investment...'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add empty option for select fields
        for field_name in ['investment_budget', 'investment_type', 'preferred_location', 'timeline']:
            self.fields[field_name].empty_label = f"Select {field_name.replace('_', ' ').title()}"
    
    def clean_property_interests(self):
        """Convert list of property interests to comma-separated string"""
        interests = self.cleaned_data.get('property_interests')
        if interests:
            return ', '.join(interests)
        return ''
    
    def save(self, commit=True):
        """Override save to handle property_interests field"""
        instance = super().save(commit=False)
        
        # Handle property interests
        interests = self.cleaned_data.get('property_interests')
        if interests:
            instance.property_interests = ', '.join(interests)
        
        if commit:
            instance.save()
        return instance

class ContactFormView(forms.Form):
    """Alternative form for contact page using regular Django Form"""
    
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)
    
    investment_budget = forms.ChoiceField(
        choices=[('', 'Select Budget Range')] + Contact.BUDGET_CHOICES,
        required=False
    )
    
    investment_type = forms.ChoiceField(
        choices=[('', 'Select Investment Type')] + Contact.INVESTMENT_TYPE_CHOICES,
        required=False
    )
    
    property_interests = forms.MultipleChoiceField(
        choices=[
            ('luxury-villa', 'Luxury Villas'),
            ('penthouse', 'Penthouses'),
            ('apartment', 'Apartments'),
            ('townhouse', 'Townhouses'),
            ('off-plan', 'Off-Plan Properties'),
            ('commercial', 'Commercial'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    preferred_location = forms.ChoiceField(
        choices=[('', 'Select Preferred Location')] + Contact.LOCATION_CHOICES,
        required=False
    )
    
    timeline = forms.ChoiceField(
        choices=[('', 'Select Timeline')] + Contact.TIMELINE_CHOICES,
        required=False
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Tell us more about your specific requirements...'
        }),
        required=False
    )