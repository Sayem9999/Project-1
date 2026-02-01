import httpx
import os
import hmac
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict

# bKash configuration
BKASH_USERNAME = os.environ.get('BKASH_USERNAME')
BKASH_PASSWORD = os.environ.get('BKASH_PASSWORD')
BKASH_APP_KEY = os.environ.get('BKASH_APP_KEY')
BKASH_APP_SECRET = os.environ.get('BKASH_APP_SECRET')
BKASH_BASE_URL = os.environ.get('BKASH_BASE_URL')

# Token cache
token_cache = {}

async def get_bkash_token() -> str:
    """Get or refresh bKash authentication token"""
    current_time = datetime.now(timezone.utc)
    
    # Check if we have a valid cached token
    if "id_token" in token_cache:
        token_data = token_cache["id_token"]
        if token_data["expires_at"] > current_time:
            return token_data["token"]
    
    # Request new token
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BKASH_BASE_URL}/tokenized/checkout/token/grant",
                json={
                    "app_key": BKASH_APP_KEY,
                    "app_secret": BKASH_APP_SECRET,
                },
                headers={
                    "username": BKASH_USERNAME,
                    "password": BKASH_PASSWORD,
                },
                timeout=30.0,
            )
            
            if response.status_code != 200:
                logging.error(f"bKash token error: {response.text}")
                raise Exception("Failed to obtain bKash token")
            
            data = response.json()
            
            # Cache the token
            token_cache["id_token"] = {
                "token": data["id_token"],
                "expires_at": current_time + timedelta(hours=1),
                "refresh_token": data.get("refresh_token"),
            }
            
            return data["id_token"]
        except Exception as e:
            logging.error(f"bKash token request failed: {str(e)}")
            raise

async def create_bkash_payment(
    amount: float,
    merchant_invoice_number: str,
    callback_url: str
) -> Dict:
    """Create a new bKash payment"""
    token = await get_bkash_token()
    
    payload = {
        "amount": str(amount),
        "merchantInvoiceNumber": merchant_invoice_number,
        "intent": "sale",
        "currency": "BDT",
        "callbackURL": callback_url,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BKASH_BASE_URL}/tokenized/checkout/create",
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-APP-Key": BKASH_APP_KEY,
                },
                timeout=30.0,
            )
            
            if response.status_code != 200:
                logging.error(f"bKash create payment error: {response.text}")
                raise Exception(response.json().get("errorMessage", "Payment creation failed"))
            
            return response.json()
        except httpx.TimeoutException:
            raise Exception("bKash service timeout")
        except Exception as e:
            logging.error(f"bKash create payment failed: {str(e)}")
            raise

async def execute_bkash_payment(payment_id: str) -> Dict:
    """Execute bKash payment after user authorization"""
    token = await get_bkash_token()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BKASH_BASE_URL}/tokenized/checkout/execute",
                json={"paymentID": payment_id},
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-APP-Key": BKASH_APP_KEY,
                },
                timeout=30.0,
            )
            
            if response.status_code != 200:
                logging.error(f"bKash execute payment error: {response.text}")
                raise Exception(response.json().get("statusMessage", "Payment execution failed"))
            
            data = response.json()
            
            # Check if payment was successful
            if data.get("statusCode") != "0000":
                raise Exception(data.get("statusMessage", "Payment failed"))
            
            return data
        except httpx.TimeoutException:
            raise Exception("bKash service timeout")
        except Exception as e:
            logging.error(f"bKash execute payment failed: {str(e)}")
            raise

async def query_bkash_payment(payment_id: str) -> Dict:
    """Query bKash payment status"""
    token = await get_bkash_token()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BKASH_BASE_URL}/tokenized/checkout/payment/status",
                json={"paymentID": payment_id},
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-APP-Key": BKASH_APP_KEY,
                },
                timeout=30.0,
            )
            
            if response.status_code != 200:
                logging.error(f"bKash query payment error: {response.text}")
                raise Exception("Payment query failed")
            
            return response.json()
        except Exception as e:
            logging.error(f"bKash query payment failed: {str(e)}")
            raise

def verify_bkash_webhook(payload: bytes, signature: str) -> bool:
    """Verify bKash webhook signature"""
    expected_signature = hmac.new(
        BKASH_APP_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
