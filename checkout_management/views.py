from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import uuid
import hashlib
from urllib.parse import quote_plus, unquote_plus
import requests
from urllib.parse import urlencode

from urllib.parse import parse_qs

#import models for creating the order
from order_management.views import create_order_from_cart
from django.contrib.auth.models import User


IN_PRODUCTION = settings.IN_PRODUCTION

# PayFast credentials
PAYFAST_MERCHANT_ID = settings.PAYFAST_TEST_MERCHANT_ID
PAYFAST_MERCHANT_KEY = settings.PAYFAST_TEST_MERCHANT_KEY

PAYFAST_URL = ""

if IN_PRODUCTION == True:
    PAYFAST_URL = "https://www.payfast.co.za/eng/process"
else:
    PAYFAST_URL = "https://sandbox.payfast.co.za/eng/process"



def checkout(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

    try:
        data = json.loads(request.body)
        total_amount = float(data.get("totalPurchaseTotal", 0))
        # Generate a unique transaction ID
        m_payment_id = str(data.get("orderNumber"))

        customer_name = str(data.get("customerName", ""))
        customer_phone = str(data.get("customerPhone", ""))
        
        request.session['customer_phone'] = customer_phone

        #-------------------------------
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        if IN_PRODUCTION == True:
            RETURN_URL = "https://heranbites.onrender.com/#/success"
            NOTIFY_URL = "https://heranbites-backend.onrender.com"
            NOTIFY_URL += "/api/ipn"
        else:
            RETURN_URL = "http://localhost:3000/#/success"

            #change below notify url to local cloudflare public url
            NOTIFY_URL = "https://availability-robust-star-dancing.trycloudflare.com" 
            NOTIFY_URL += "/api/ipn"
            
        #------------------------------
        # Build PayFast payload
        payload = {
            "custom_str1": session_key,
            "custom_str2": customer_name,
            "custom_str3": customer_phone,
            "custom_str4": total_amount,
            "merchant_id": PAYFAST_MERCHANT_ID,
            "merchant_key": PAYFAST_MERCHANT_KEY,
            "return_url": RETURN_URL,
            "cancel_url": "https://yourdomain.com/payment-cancel",
            #"notify_url": "https://heranbites-backend.onrender.com/api/ipn",
            "notify_url": NOTIFY_URL,
            "m_payment_id": m_payment_id,
            "amount": "%.2f" % total_amount,
            "item_name": f"Order #{m_payment_id}",
            "name_first": "John",
            "name_last": "Doe",
            "email_address": "john@example.com",
        }

        # Construct PayFast URL
        # Encode all parameters properly
        payment_url = f"{PAYFAST_URL}?{urlencode(payload)}"
        
        return JsonResponse({"success": True, "payment_url": payment_url})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@csrf_exempt
def payfast_ipn(request):
    if request.method != "POST":
        return HttpResponse("Invalid request method", status=405)

    # Convert POST body to dict
    raw_body = request.body.decode("utf-8")
    data = {k: v[0] for k, v in parse_qs(raw_body).items()}

    # Validate with PayFast
    response = requests.post(
        "https://sandbox.payfast.co.za/eng/query/validate",  # change to production URL in prod
        data=data
    )

    if response.text == "VALID":
        if data.get("payment_status") == "COMPLETE":
            print("Successful payment")
            session_key = data.get("custom_str1")

            #CREATE ORDER IN DATABASE once payment is successful
            customer_name = data.get("custom_str2")
            customer_phone = data.get("custom_str3")
            total_amount = data.get("custom_str4")

            #Call the function from order_management
            order = create_order_from_cart(session_key, customer_name, customer_phone, total_amount, payment_method="card")

            if order:
                print(f"ORDER created successfully!")
            else:
                print("Failed to create order or cart empty.")
            
            return HttpResponse("Payment received", status=200)
        else:
            print("Payment not complete")
            return HttpResponse("Payment not complete", status=400)
    else:
        print("IPN could not be validated by PayFast")
        return HttpResponse("Invalid IPN", status=400)