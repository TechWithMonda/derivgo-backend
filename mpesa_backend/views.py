from django.http import JsonResponse
from datetime import datetime
import requests
import base64
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def mpesa_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            phone = data.get('phone')
            amount = data.get("amount")  # Corrected from `request.data.get("amount")`

            if not phone or not amount:
                return JsonResponse({"error": "Phone and amount are required"}, status=400)

            # Convert amount to integer (rounding if decimal)
            amount = int(float(amount))  # Ensures 355.99 -> 356

            # 🛠 Fetch credentials from settings
            consumer_key = settings.MPESA_CONFIGS['CONSUMER_KEY']
            consumer_secret = settings.MPESA_CONFIGS['CONSUMER_SECRET']
            shortcode = settings.MPESA_CONFIGS['BUSINESS_SHORT_CODE']
            passkey = settings.MPESA_CONFIGS['PASS_KEY']
            callback_url = settings.MPESA_CONFIGS['CALLBACK_URL']

            # 🌐 Get access token
            auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
            auth = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
            headers = {'Authorization': f'Basic {auth}'}
            token_response = requests.get(auth_url, headers=headers)
            access_token = token_response.json().get('access_token')

            if not access_token:
                return JsonResponse({'error': 'Failed to retrieve access token'}, status=400)

            # ⏲️ Generate password and timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()

            # 📲 Prepare payment request payload
            stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
            stk_headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            stk_payload = {
                "BusinessShortCode": shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": settings.MPESA_CONFIGS['TRANSACTION_TYPE'],
                "Amount": amount,
                "PartyA": phone,
                "PartyB": shortcode,
                "PhoneNumber": phone,
                "CallBackURL": callback_url,
                "AccountReference": "Test",
                "TransactionDesc": "Test Payment"
            }

            response = requests.post(stk_url, json=stk_payload, headers=stk_headers)
            return JsonResponse(response.json())

        except ValueError:
            return JsonResponse({"error": "Invalid amount format"}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("M-Pesa Callback Data:", data)  # Debugging: Log received data

            # Extract transaction details
            result_code = data.get("Body", {}).get("stkCallback", {}).get("ResultCode", "")
            result_desc = data.get("Body", {}).get("stkCallback", {}).get("ResultDesc", "")

            if result_code == 0:
                return JsonResponse({"message": "Payment successful", "status": "success"})
            else:
                return JsonResponse({"message": f"Payment failed: {result_desc}", "status": "failed"})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)
