from django.core.management.base import BaseCommand
from exclusive_properties.models import ExclusiveProperty, PropertyAmenity, ExclusivePropertyAmenity
from django.utils.text import slugify
import random

class Command(BaseCommand):
    help = 'Import sample exclusive properties for demonstration'
    
    def handle(self, *args, **options):
        # Create sample amenities
        amenities_data = [
            ('Swimming Pool', 'fas fa-swimming-pool', 'Recreation'),
            ('Gym & Fitness', 'fas fa-dumbbell', 'Recreation'),
            ('Covered Parking', 'fas fa-car', 'Convenience'),
            ('24/7 Security', 'fas fa-shield-alt', 'Security'),
            ('Concierge Service', 'fas fa-concierge-bell', 'Service'),
            ('Garden & Landscaping', 'fas fa-leaf', 'Recreation'),
            ('Children\'s Playground', 'fas fa-child', 'Recreation'),
            ('Business Center', 'fas fa-briefcase', 'Business'),
            ('Spa & Wellness', 'fas fa-spa', 'Recreation'),
            ('Rooftop Terrace', 'fas fa-building', 'Recreation'),
        ]
        
        for name, icon, category in amenities_data:
            PropertyAmenity.objects.get_or_create(
                name=name,
                defaults={'icon': icon, 'category': category}
            )
        
        # Create sample properties
        sample_properties = [
            {
                'title': 'Luxury Marina Penthouse',
                'property_type': 'penthouse',
                'district': 'Dubai Marina',
                'bedrooms': 3,
                'bathrooms': 4,
                'area_sqft': 2400,
                'price': 2850000,
                'short_description': 'Stunning penthouse with panoramic marina views and premium finishes.',
                'description': '<p>Experience luxury living at its finest in this spectacular penthouse...</p>'
            },
            {
                'title': 'Contemporary Jumeirah Villa',
                'property_type': 'villa',
                'district': 'Jumeirah',
                'bedrooms': 5,
                'bathrooms': 6,
                'area_sqft': 4800,
                'price': 4200000,
                'short_description': 'Architecturally designed villa with private beach access.',
                'description': '<p>This contemporary villa offers unparalleled luxury...</p>'
            }
        ]
        
        for prop_data in sample_properties:
            prop_data['slug'] = slugify(f"{prop_data['title']}-{prop_data['district']}")
            property_obj, created = ExclusiveProperty.objects.get_or_create(
                title=prop_data['title'],
                defaults=prop_data
            )
            
            if created:
                # Add random amenities
                amenities = ExclusivePropertyAmenity.objects.order_by('?')[:5]
                property_obj.amenities.set(amenities)
                self.stdout.write(
                    self.style.SUCCESS(f'Created property: {property_obj.title}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully imported sample exclusive properties')
        )