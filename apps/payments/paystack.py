import hmac
import hashlib
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class PaystackService:
    def __init__(self):
        self.secret_key = getattr(settings, 'PAYSTACK_SECRET_KEY', '')
        self.public_key = getattr(settings, 'PAYSTACK_PUBLIC_KEY', '')
        self.initialize_url = getattr(settings, 'PAYSTACK_INITIALIZE_URL', 'https://api.paystack.co/transaction/initialize')
        self.verify_url = getattr(settings, 'PAYSTACK_VERIFY_URL', 'https://api.paystack.co/transaction/verify/')

    def initialize_transaction(self, email, amount_in_kobo, reference, callback_url, metadata=None):
        """
        Initializes transaction with Paystack API.
        Returns: (success: bool, data_or_error: dict)
        """
        headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'email': email,
            'amount': amount_in_kobo,
            'reference': reference,
            'callback_url': callback_url,
            'metadata': metadata or {},
        }

        try:
            response = requests.post(self.initialize_url, json=payload, headers=headers, timeout=15)
            res_json = response.json()
            if response.status_code == 200 and res_json.get('status') is True:
                return True, res_json.get('data')
            else:
                logger.warning(f"Paystack API init non-200: {res_json}")
                return False, res_json.get('message', 'Failed to initialize transaction')
        except Exception as e:
            logger.error(f"Paystack init network exception: {e}")
            # If network error or test keys not connected to internet, return graceful notice
            return False, str(e)

    def verify_transaction(self, reference):
        """
        Verifies transaction server-side against Paystack API.
        Returns: (success: bool, data: dict)
        """
        headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
        }
        url = f"{self.verify_url.rstrip('/')}/{reference}"

        try:
            response = requests.get(url, headers=headers, timeout=15)
            res_json = response.json()
            if response.status_code == 200 and res_json.get('status') is True:
                data = res_json.get('data', {})
                if data.get('status') == 'success':
                    return True, data
                return False, data
            return False, res_json
        except Exception as e:
            logger.error(f"Paystack verify network error: {e}")
            return False, {'error': str(e)}

    def verify_webhook_signature(self, request_body, signature):
        """
        Validates HMAC SHA512 signature for Paystack webhooks.
        """
        if not signature or not self.secret_key:
            return False
        computed_signature = hmac.new(
            self.secret_key.encode('utf-8'),
            msg=request_body,
            digestmod=hashlib.sha512
        ).hexdigest()
        return hmac.compare_digest(computed_signature, signature)
