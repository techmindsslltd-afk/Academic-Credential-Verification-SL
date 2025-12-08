# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present TechMinds SL Ltd
"""

import requests
import json
import logging
from django.conf import settings
from decimal import Decimal

logger = logging.getLogger(__name__)


class MonimePaymentService:
    """Service class for handling Monime payment operations"""
    
    def __init__(self):
        # Monime API base URL - this is the main endpoint for all Monime API calls
        # According to Monime docs: https://docs.monime.io/apis
        # Both Live and Test environments use the same base URL
        self.base_url = "https://api.monime.io"
        
        # Test token for development/testing environment
        # This token is used when testing payments without real money transactions
        # Retrieved from Django settings with empty string as fallback if not configured
        self.test_token = getattr(settings, 'MONIME_TEST_TOKEN', '')
        
        # Live token for production environment
        # This token is used for real money transactions in production
        # Retrieved from Django settings with empty string as fallback if not configured
        self.live_token = getattr(settings, 'MONIME_LIVE_TOKEN', '')
        
        # Environment flag to determine which token to use
        # False = Use test token (development/sandbox mode)
        # True = Use live token (production mode with real money)
        # Retrieved from Django settings with False as default (safer default)
        self.is_live = getattr(settings, 'MONIME_LIVE_MODE', False)
        
        
    def get_headers(self):
        """
        Get headers for API requests
        
        Returns:
            dict: HTTP headers required for Monime API authentication
        """
        # Select the appropriate token based on environment
        # If is_live is True, use live_token for production
        # If is_live is False, use test_token for development/testing
        token = self.live_token if self.is_live else self.test_token
        
        return {
            # Bearer token authentication as required by Monime API
            # Format: "Bearer {your-token-here}"
            'Authorization': f'Bearer {token}',
            
            # Monime Space ID header - required for space-scoped endpoints
            # This identifies which Monime space/organization the request belongs to
            'Monime-Space-Id': getattr(settings, 'MONIME_SPACE_ID', 'your-space-id'),
            
            # Content-Type for JSON requests (Monime API expects JSON)
            'Content-Type': 'application/json',
            
            # Accept header to specify we expect JSON responses
            'Accept': 'application/json'
        }
    
    def create_payment(self, donation_data):
        """
        Create a payment for donation using Monime API
        
        Args:
            donation_data (dict): Donation information including amount, currency, etc.
            
        Returns:
            dict: Response from Monime API
        """
        # Check if we're in test mode - Monime doesn't support test endpoints
        if not self.is_live:
            logger.info("Monime test mode not supported - using enhanced mock payment system")
            return self._create_enhanced_mock_payment(donation_data)
        
        # Live mode - try real Monime API
        try:
            # Convert amount to minor currency units (cents)
            amount_cents = int(float(donation_data['amount']) * 100)
            
            # Try different Monime API endpoints
            endpoints_to_try = [
                f"{self.base_url}/checkout/session",
                f"{self.base_url}/checkout/public/sessions",
                f"{self.base_url}/v1/payments",
                f"{self.base_url}/v1/checkout/sessions",
                f"{self.base_url}/v1/payins",
                f"{self.base_url}/payments",

            ]
            
            payload = {
                "amount": amount_cents,
                "currency": donation_data.get('currency', 'USD'),
                "description": f"Donation to {donation_data.get('organization_name', 'Apple of God Foundation')}",
                "customer": {
                    "email": donation_data['email'],
                    "name": f"{donation_data['first_name']} {donation_data['last_name']}",
                    "phone": donation_data.get('phone', ''),
                },
                "metadata": {
                    "donation_id": donation_data.get('donation_id'),
                    "donor_name": f"{donation_data['first_name']} {donation_data['last_name']}",
                    "is_organization": donation_data.get('is_organization', False),
                    "organization_name": donation_data.get('organization_name', ''),
                    "is_anonymous": donation_data.get('is_anonymous', False),
                },
                "success_url": f"{settings.SITE_URL}/donate/success/?payment_id={{payment_id}}",
                "cancel_url": f"{settings.SITE_URL}/donate/cancel/?payment_id={{payment_id}}",
                "webhook_url": f"{settings.SITE_URL}/donate/webhook/",
            }
            
            # Add address information if available
            if donation_data.get('street_address'):
                payload["customer"]["address"] = {
                    "line1": donation_data['street_address'],
                    "line2": donation_data.get('apt_suite', ''),
                    "city": donation_data.get('city', ''),
                    "state": donation_data.get('state', ''),
                    "country": donation_data.get('country', 'US'),
                    "postal_code": donation_data.get('postal_code', ''),
                }
            
            # Try each endpoint until one works
            for endpoint in endpoints_to_try:
                logger.info(f"Trying Monime endpoint: {endpoint}")
                
                response = requests.post(
                    endpoint,
                    headers=self.get_headers(),
                    json=payload,
                    timeout=30
                )
                
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response body: {response.text}")
                
                if response.status_code == 200 or response.status_code == 201:
                    response_data = response.json()
                    return {
                        'success': True,
                        'data': response_data,
                        'payment_url': response_data.get('url') or response_data.get('checkout_url') or response_data.get('payment_url'),
                        'payment_id': response_data.get('id') or response_data.get('payment_id')
                    }
                elif response.status_code == 403:
                    # This endpoint doesn't support test mode, try next one
                    logger.warning(f"Endpoint {endpoint} doesn't support test mode, trying next...")
                    continue
                else:
                    logger.warning(f"Endpoint {endpoint} failed with status {response.status_code}")
                    continue
            
            # If all endpoints failed, return the last error
            logger.error(f"All Monime endpoints failed. Last response: {response.status_code} - {response.text}")
            return {
                'success': False,
                'error': f"All Monime endpoints failed. Last error: {response.status_code}",
                'details': response.text
            }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Monime API request failed: {str(e)}")
            return {
                'success': False,
                'error': 'Network error',
                'details': str(e)
            }
        except Exception as e:
            logger.error(f"Monime API unexpected error: {str(e)}")
            return {
                'success': False,
                'error': 'Unexpected error',
                'details': str(e)
            }
    
    def _create_enhanced_mock_payment(self, donation_data):
        """
        Create an enhanced mock payment for testing purposes
        This simulates Monime API response structure
        
        Args:
            donation_data (dict): Donation information
            
        Returns:
            dict: Mock payment response
        """
        import uuid
        import time
        from datetime import datetime
        
        # Generate mock payment ID that looks like Monime format
        payment_id = f"pay_{uuid.uuid4().hex[:16]}"
        
        # Create mock payment URL (simulates Monime checkout)
        mock_payment_url = f"{settings.SITE_URL}/donate/mock-payment/?payment_id={payment_id}&amount={donation_data['amount']}&donation_id={donation_data.get('donation_id', '')}"
        
        # Create realistic Monime-style response
        mock_response = {
            'id': payment_id,
            'object': 'payment',
            'amount': int(float(donation_data['amount']) * 100),  # Amount in cents
            'currency': donation_data.get('currency', 'USD'),
            'status': 'pending',
            'description': f"Donation to {donation_data.get('organization_name', 'Apple of God Foundation')}",
            'customer': {
                'email': donation_data['email'],
                'name': f"{donation_data['first_name']} {donation_data['last_name']}",
                'phone': donation_data.get('phone', ''),
            },
            'metadata': {
                'donation_id': donation_data.get('donation_id'),
                'donor_name': f"{donation_data['first_name']} {donation_data['last_name']}",
                'is_organization': donation_data.get('is_organization', False),
                'organization_name': donation_data.get('organization_name', ''),
                'is_anonymous': donation_data.get('is_anonymous', False),
            },
            'url': mock_payment_url,
            'checkout_url': mock_payment_url,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'expires_at': (datetime.now().timestamp() + 1800),  # 30 minutes from now
        }
        
        logger.info(f"Created enhanced mock payment: {payment_id} for amount: ${donation_data['amount']}")
        logger.info(f"Mock payment URL: {mock_payment_url}")
        
        return {
            'success': True,
            'data': mock_response,
            'payment_url': mock_payment_url,
            'payment_id': payment_id
        }
    
    def _create_mock_payment(self, donation_data):
        """
        Create a mock payment for testing purposes (legacy method)
        
        Args:
            donation_data (dict): Donation information
            
        Returns:
            dict: Mock payment response
        """
        import uuid
        import time
        
        # Generate mock payment ID
        payment_id = f"mock_pay_{uuid.uuid4().hex[:16]}"
        
        # Create mock payment URL (simulates Monime checkout)
        mock_payment_url = f"{settings.SITE_URL}/donate/mock-payment/?payment_id={payment_id}&amount={donation_data['amount']}&donation_id={donation_data.get('donation_id', '')}"
        
        logger.info(f"Created mock payment: {payment_id} for amount: {donation_data['amount']}")
        
        return {
            'success': True,
            'data': {
                'id': payment_id,
                'url': mock_payment_url,
                'status': 'pending',
                'amount': donation_data['amount'],
                'currency': donation_data.get('currency', 'USD')
            },
            'payment_url': mock_payment_url,
            'payment_id': payment_id
        }
    
    def get_payment_status(self, session_id):
        """
        Get payment status for a checkout session
        
        Args:
            session_id (str): Checkout session ID
            
        Returns:
            dict: Payment status information
        """
        try:
            response = requests.get(
                f"{self.base_url}/checkout-sessions/{session_id}",
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                logger.error(f"Monime API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code}",
                    'details': response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Monime API request failed: {str(e)}")
            return {
                'success': False,
                'error': 'Network error',
                'details': str(e)
            }
        except Exception as e:
            logger.error(f"Monime API unexpected error: {str(e)}")
            return {
                'success': False,
                'error': 'Unexpected error',
                'details': str(e)
            }
    
    def verify_webhook_signature(self, payload, signature):
        """
        Verify webhook signature (if Monime provides signature verification)
        
        Args:
            payload (str): Raw webhook payload
            signature (str): Webhook signature
            
        Returns:
            bool: True if signature is valid
        """
        # Note: This would need to be implemented based on Monime's webhook signature verification
        # For now, we'll return True as a placeholder
        return True
    
    def process_webhook(self, webhook_data):
        """
        Process webhook data from Monime
        
        Args:
            webhook_data (dict): Webhook payload from Monime
            
        Returns:
            dict: Processing result
        """
        try:
            event_type = webhook_data.get('type') or webhook_data.get('event')
            payment_id = webhook_data.get('data', {}).get('id')
            
            if event_type == 'payment.completed':
                # Payment was successful
                return {
                    'success': True,
                    'status': 'completed',
                    'payment_id': payment_id
                }
            elif event_type == 'payment.failed':
                # Payment failed
                return {
                    'success': True,
                    'status': 'failed',
                    'payment_id': payment_id
                }
            elif event_type == 'payment.cancelled':
                # Payment cancelled
                return {
                    'success': True,
                    'status': 'cancelled',
                    'payment_id': payment_id
                }
            elif event_type == 'payment.expired':
                # Payment expired
                return {
                    'success': True,
                    'status': 'expired',
                    'payment_id': payment_id
                }
            else:
                # Other event types
                return {
                    'success': True,
                    'status': 'unknown',
                    'event_type': event_type,
                    'payment_id': payment_id
                }
                
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return {
                'success': False,
                'error': 'Webhook processing failed',
                'details': str(e)
            }
