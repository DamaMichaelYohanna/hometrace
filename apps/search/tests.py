from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from properties.models import Property, PropertyCategory


class SearchTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.agent = User.objects.create_user(
            email='search_agent@hometrace.ng',
            password='Password123!',
            full_name='Search Agent',
            role=User.Role.AGENT
        )
        self.cat1 = PropertyCategory.objects.create(name='Apartments')
        self.cat2 = PropertyCategory.objects.create(name='Houses')

        Property.objects.create(
            agent=self.agent,
            category=self.cat1,
            title='Cozy Flat in Ikeja',
            description='Close to Lagos airport',
            listing_purpose='for_rent',
            state='Lagos',
            city='Ikeja',
            neighbourhood='GRA',
            price=Decimal('3000000.00'),
            bedrooms=2,
            approval_status=Property.ApprovalStatus.APPROVED,
            availability_status=Property.AvailabilityStatus.AVAILABLE,
        )

        Property.objects.create(
            agent=self.agent,
            category=self.cat2,
            title='Palatial Villa in Maitama',
            description='Prime Abuja residence',
            listing_purpose='for_sale',
            state='Abuja FCT',
            city='Abuja',
            neighbourhood='Maitama',
            price=Decimal('200000000.00'),
            bedrooms=5,
            approval_status=Property.ApprovalStatus.APPROVED,
            availability_status=Property.AvailabilityStatus.AVAILABLE,
        )

    def test_search_by_keyword(self):
        response = self.client.get(reverse('search') + '?q=Ikeja')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cozy Flat in Ikeja')
        self.assertNotContains(response, 'Palatial Villa in Maitama')

    def test_search_by_state(self):
        response = self.client.get(reverse('search') + '?state=Abuja+FCT')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Palatial Villa in Maitama')
        self.assertNotContains(response, 'Cozy Flat in Ikeja')

    def test_search_by_price_range(self):
        response = self.client.get(reverse('search') + '?max_price=5000000')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cozy Flat in Ikeja')
        self.assertNotContains(response, 'Palatial Villa in Maitama')
