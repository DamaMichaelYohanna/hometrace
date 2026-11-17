from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from properties.models import Property, PropertyCategory
from favorites.models import Favorite


class FavoritesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.agent = User.objects.create_user(
            email='fav_agent@hometrace.ng',
            password='Password123!',
            full_name='Fav Agent',
            role=User.Role.AGENT
        )
        self.buyer = User.objects.create_user(
            email='fav_buyer@hometrace.ng',
            password='Password123!',
            full_name='Fav Buyer',
            role=User.Role.BUYER
        )
        self.cat = PropertyCategory.objects.create(name='Terrace')
        self.prop = Property.objects.create(
            agent=self.agent,
            category=self.cat,
            title='Lekki Phase 1 Terrace Home',
            description='Prime home',
            listing_purpose='for_rent',
            state='Lagos',
            city='Lekki',
            neighbourhood='Lekki 1',
            price=Decimal('5000000.00'),
            approval_status=Property.ApprovalStatus.APPROVED,
            availability_status=Property.AvailabilityStatus.AVAILABLE,
        )

    def test_toggle_favorite_ajax(self):
        self.client.login(email='fav_buyer@hometrace.ng', password='Password123!')
        
        # 1. Toggle ON
        res = self.client.get(reverse('toggle_favorite', kwargs={'property_id': self.prop.id}) + '?format=json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['saved'])
        self.assertEqual(data['total_favorites'], 1)
        self.assertTrue(Favorite.objects.filter(user=self.buyer, property=self.prop).exists())

        # 2. Toggle OFF
        res = self.client.get(reverse('toggle_favorite', kwargs={'property_id': self.prop.id}) + '?format=json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data['saved'])
        self.assertEqual(data['total_favorites'], 0)
        self.assertFalse(Favorite.objects.filter(user=self.buyer, property=self.prop).exists())
