from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, AgentProfile
from payments.models import Payment


class PaymentsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.agent = User.objects.create_user(
            email='pay_agent@hometrace.ng',
            password='Password123!',
            full_name='Payment Agent',
            role=User.Role.AGENT
        )
        self.agent_profile, _ = AgentProfile.objects.get_or_create(user=self.agent)

    def test_payment_initialization(self):
        self.client.login(email='pay_agent@hometrace.ng', password='Password123!')
        res = self.client.post(reverse('payment_checkout'), {
            'purpose': Payment.Purpose.AGENT_VERIFICATION,
        })
        # Should render sandbox checkout or redirect to authorization url
        self.assertIn(res.status_code, [200, 302])
        self.assertTrue(Payment.objects.filter(user=self.agent, purpose=Payment.Purpose.AGENT_VERIFICATION).exists())

    def test_demo_simulated_payment_verification_and_fulfillment(self):
        payment = Payment.objects.create(
            user=self.agent,
            reference='HT-TEST-VERIFY-123',
            amount=Decimal('15000.00'),
            currency='NGN',
            purpose=Payment.Purpose.AGENT_VERIFICATION,
            status=Payment.Status.PENDING
        )
        self.client.login(email='pay_agent@hometrace.ng', password='Password123!')
        
        # Hit callback with demo=1 simulation flag
        res = self.client.get(reverse('payment_callback') + '?reference=HT-TEST-VERIFY-123&demo=1')
        self.assertEqual(res.status_code, 302)

        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.SUCCESS)

        self.agent_profile.refresh_from_db()
        self.assertTrue(self.agent_profile.is_verified_agent)
