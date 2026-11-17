from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, AgentProfile, BuyerProfile


class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.agent_user = User.objects.create_user(
            email='testagent@hometrace.ng',
            password='TestPassword123!',
            full_name='Test Agent',
            role=User.Role.AGENT,
            phone_number='08031234567'
        )
        self.buyer_user = User.objects.create_user(
            email='testbuyer@hometrace.ng',
            password='TestPassword123!',
            full_name='Test Buyer',
            role=User.Role.BUYER,
            phone_number='08091234567'
        )

    def test_user_creation_and_roles(self):
        self.assertTrue(self.agent_user.is_agent)
        self.assertFalse(self.agent_user.is_buyer)
        self.assertTrue(self.buyer_user.is_buyer)
        self.assertFalse(self.buyer_user.is_agent)

    def test_profile_auto_generation_via_signals(self):
        self.assertTrue(hasattr(self.agent_user, 'agent_profile'))
        self.assertTrue(hasattr(self.buyer_user, 'buyer_profile'))

    def test_login_flow(self):
        response = self.client.post(reverse('login'), {
            'email': 'testagent@hometrace.ng',
            'password': 'TestPassword123!',
        })
        self.assertEqual(response.status_code, 302)
        # Should redirect to dashboard_dispatch
        self.assertIn(reverse('dashboard_dispatch'), response.url)

    def test_duplicate_email_registration_prevention(self):
        response = self.client.post(reverse('register'), {
            'email': 'testagent@hometrace.ng',
            'full_name': 'Another Person',
            'phone_number': '08021234567',
            'role': User.Role.BUYER,
            'password': 'Password1234!',
            'confirm_password': 'Password1234!',
            'agree_terms': True,
        })
        # Should re-render with errors
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'An account with this email address already exists.')

    def test_role_based_redirects(self):
        # Login as agent
        self.client.login(email='testagent@hometrace.ng', password='TestPassword123!')
        response = self.client.get(reverse('dashboard_dispatch'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('agent_overview'), response.url)
