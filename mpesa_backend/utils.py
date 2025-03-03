import requests
import datetime
import base64
MPESA_CONFIGS = {
    'CONSUMER_KEY': 'your_consumer_key',
    'CONSUMER_SECRET': 'your_consumer_secret',
    'BUSINESS_SHORT_CODE': '174379',
    'PASS_KEY': 'your_pass_key',
    'TRANSACTION_TYPE': 'CustomerPayBillOnline',
    'CALLBACK_URL': 'https://your-domain.com/api/mpesa/callback/',
}

class MpesaGateway:
    def __init__(self):
        self.business_shortcode = MPESA_CONFIGS['BUSINESS_SHORT_CODE']
        self.consumer_key = MPESA_CONFIGS['CONSUMER_KEY']
        self.consumer_secret = MPESA_CONFIGS['CONSUMER_SECRET']
        self.pass_key = MPESA_CONFIGS['PASS_KEY']
        
    def get_access_token(self):
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        auth = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
        headers = {'Authorization': f'Basic {auth}'}
        
        response = requests.get(url, headers=headers)
        return response.json()['access_token']
    
    def generate_password(self):
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.business_shortcode}{self.pass_key}{timestamp}"
        return base64.b64encode(password_str.encode()).decode(), timestamp
    
    def initiate_stk_push(self, phone_number, amount, account_reference, transaction_desc):
        access_token = self.get_access_token()
        password, timestamp = self.generate_password()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        
        payload = {
            "BusinessShortCode": self.business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": MPESA_CONFIGS['TRANSACTION_TYPE'],
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": self.business_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": MPESA_CONFIGS['CALLBACK_URL'],
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }
        
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        response = requests.post(url, json=payload, headers=headers)
        return response.json()