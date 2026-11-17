from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from properties.models import Property, PropertyCategory, Amenity


class PropertiesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.agent = User.objects.create_user(
            email='agent_prop_test@hometrace.ng',
            password='TestPassword123!',
            full_name='Test Agent Properties',
            role=User.Role.AGENT,
            phone_number='08031234567'
        )
        self.category = PropertyCategory.objects.create(name='Duplexes', icon_name='home')
        self.amenity = Amenity.objects.create(name='24/7 Security', category='security')

        self.property = Property.objects.create(
            agent=self.agent,
            category=self.category,
            title='Stunning 4 Bedroom Duplex in Lekki',
            description='Executive residence with modern finishes.',
            listing_purpose=Property.Purpose.FOR_SALE,
            state='Lagos',
            city='Lekki',
            neighbourhood='Lekki Phase 1',
            price=Decimal('150000000.00'),
            bedrooms=4,
            bathrooms=4,
            approval_status=Property.ApprovalStatus.APPROVED,
            availability_status=Property.AvailabilityStatus.AVAILABLE,
        )
        self.property.amenities.add(self.amenity)

    def test_property_slug_generation(self):
        self.assertTrue(self.property.slug.startswith('stunning-4-bedroom-duplex-in-lekki'))

    def test_public_property_detail_view(self):
        response = self.client.get(reverse('property_detail', kwargs={'slug': self.property.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Stunning 4 Bedroom Duplex in Lekki')
        self.assertContains(response, '150,000,000')

    def test_unapproved_property_hidden_from_public(self):
        unapproved = Property.objects.create(
            agent=self.agent,
            category=self.category,
            title='Secret Unapproved Listing',
            description='Not yet verified',
            listing_purpose=Property.Purpose.FOR_RENT,
            state='Abuja FCT',
            city='Maitama',
            neighbourhood='Maitama',
            price=Decimal('5000000.00'),
            approval_status=Property.ApprovalStatus.PENDING,
            availability_status=Property.AvailabilityStatus.AVAILABLE,
        )
        response = self.client.get(reverse('property_detail', kwargs={'slug': unapproved.slug}))
        # Anonymous should be redirected with warning
        self.assertEqual(response.status_code, 302)
