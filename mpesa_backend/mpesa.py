import requests
import base64
from datetime import datetime
from django.conf import settings

def generate_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    auth_string = base64.b64encode(
        f"{consumer_key}:{consumer_secret}".encode()
    ).decode()
    
    headers = {"Authorization": f"Basic {auth_string}"}
    
    try:
        response = requests.get(auth_url, headers=headers)
        response.raise_for_status()  # Raise exception for non-200 status codes
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to generate access token: {str(e)}")

def format_phone_number(phone_number):
    """Convert phone number to required format (254...)"""
    if phone_number.startswith("+"):
        phone_number = phone_number[1:]
    if phone_number.startswith("0"):
        phone_number = "254" + phone_number[1:]
    return phone_number

def initiate_stk_push(phone_number, amount, reference):
    try:
        access_token = generate_access_token()
        
        formatted_phone = format_phone_number(phone_number)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(float(amount)),
            "PartyA": formatted_phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": formatted_phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": reference,
            "TransactionDesc": f"Payment for {reference}"
        }
        import json
        print("STK Payload:", json.dumps(payload, indent=4))

        
        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers
        )
        
        return response.json()
        
    except Exception as e:
        raise Exception(f"STK push failed: {str(e)}")
