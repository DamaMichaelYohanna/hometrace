from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from properties.models import Property, PropertyCategory
from messaging.models import Conversation, Message


class MessagingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.agent = User.objects.create_user(
            email='msg_agent@hometrace.ng',
            password='Password123!',
            full_name='Msg Agent',
            role=User.Role.AGENT
        )
        self.buyer = User.objects.create_user(
            email='msg_buyer@hometrace.ng',
            password='Password123!',
            full_name='Msg Buyer',
            role=User.Role.BUYER
        )
        self.cat = PropertyCategory.objects.create(name='Flats')
        self.prop = Property.objects.create(
            agent=self.agent,
            category=self.cat,
            title='Executive Flat',
            description='Prime home',
            listing_purpose='for_rent',
            state='Lagos',
            city='Ikeja',
            neighbourhood='GRA',
            price=Decimal('2000000.00'),
            approval_status=Property.ApprovalStatus.APPROVED,
            availability_status=Property.AvailabilityStatus.AVAILABLE,
        )

    def test_conversation_and_messaging_flow(self):
        self.client.login(email='msg_buyer@hometrace.ng', password='Password123!')
        
        # Send enquiry from buyer to agent
        response = self.client.post(reverse('send_enquiry', kwargs={'property_slug': self.prop.slug}), {
            'subject': 'Inspection Request',
            'message': 'Can I inspect this flat tomorrow afternoon?',
        })
        self.assertEqual(response.status_code, 302)

        conv = Conversation.objects.filter(buyer=self.buyer, agent=self.agent).first()
        self.assertIsNotNone(conv)
        self.assertEqual(conv.messages.count(), 1)
        self.assertIn('Can I inspect this flat', conv.messages.first().body)
