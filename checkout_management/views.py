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
from checkout_management.models import CHECKOUT
from tenant_management.models import TENANT

from django.db import transaction

IN_PRODUCTION = settings.IN_PRODUCTION

# PayFast credentials


PAYFAST_URL = ""

if IN_PRODUCTION == True:
	PAYFAST_MERCHANT_ID = settings.PAYFAST_LIVE_MERCHANT_ID
	PAYFAST_MERCHANT_KEY = settings.PAYFAST_LIVE_MERCHANT_KEY
	
	PAYFAST_URL = "https://www.payfast.co.za/eng/process"
	PAYFAST_URL_VALIDATE = "https://www.payfast.co.za/eng/query/validate"
else:
	PAYFAST_MERCHANT_ID = settings.PAYFAST_TEST_MERCHANT_ID
	PAYFAST_MERCHANT_KEY = settings.PAYFAST_TEST_MERCHANT_KEY
	
	PAYFAST_URL = "https://sandbox.payfast.co.za/eng/process"
	PAYFAST_URL_VALIDATE = "https://sandbox.payfast.co.za/eng/query/validate"



def checkout(request, slug):
	if request.method != "POST":
		return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

	try:
		data = json.loads(request.body)
		total_amount = float(data.get("totalPurchaseTotal", 0))
		customer_name = str(data.get("customerName", ""))
		customer_phone = str(data.get("customerPhone", ""))
			
		request.session["customer_phone"] = customer_phone

		#-------------------------------
		if not request.session.session_key:
			request.session.create()
		session_key = request.session.session_key

		#create checkout for customer
		tenant = TENANT.objects.get(slug=slug)

		checkout = CHECKOUT.objects.create(
			tenant=tenant,
			session_key=session_key,
			customer_phone=customer_phone,
			customer_name=customer_name,
			total_amount=total_amount
		)
		
		# Generate a unique transaction ID
		m_payment_id = str(uuid.uuid4())

		

		if IN_PRODUCTION == True:
			RETURN_URL = "https://heranbites.onrender.com/success"
			NOTIFY_URL = "https://heranbites-backend.onrender.com"
			CANCEL_URL = "https://heranbites.onrender.com/failure"
		else:
			RETURN_URL = "http://localhost:3000/success"
			#change below notify url to local cloudflare public url
			NOTIFY_URL = "https://appropriations-characteristics-lightbox-conferencing.trycloudflare.com"
			CANCEL_URL = "http://localhost:3000/failure"
		
		NOTIFY_URL += "/api/ipn"
		
		#------------------------------
		# Build PayFast payload
		payload = {
			"custom_str1": session_key,
			"custom_str2": slug,

			"merchant_id": PAYFAST_MERCHANT_ID,
			"merchant_key": PAYFAST_MERCHANT_KEY,

			"return_url": RETURN_URL,
			"cancel_url": CANCEL_URL,
			"notify_url": NOTIFY_URL,

			"m_payment_id": m_payment_id,
			"amount": "%.2f" % total_amount,
			"item_name": f"Order #{m_payment_id}",

			"name_first": customer_name or "Customer",
			"name_last": "User",
			"email_address": "noemail@yourapp.com",
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

	raw_body = request.body.decode("utf-8")
	data = {k: v[0] for k, v in parse_qs(raw_body).items()}

	# ✅ Validate with PayFast
	response = requests.post(
		PAYFAST_URL_VALIDATE,
		data=data
	)

	if response.text != "VALID":
		return HttpResponse("Invalid IPN", status=400)

	if data.get("payment_status") != "COMPLETE":
		return HttpResponse("Payment not complete", status=400)

	# ✅ Extract identifiers
	session_key = data.get("custom_str1")
	slug = data.get("custom_str2")

	if not session_key or not slug:
		return HttpResponse("Missing identifiers", status=400)

	# 🔒 LOCK checkout row
	with transaction.atomic():
		checkout = CHECKOUT.objects.select_for_update().filter(
			session_key=session_key,
			tenant__slug=slug
		).first()

		if not checkout:
			return HttpResponse("No checkout found", status=404)

		# 🚫 Prevent duplicate processing
		if checkout.status == "paid":
			return HttpResponse("Already processed", status=200)

		# ✅ Mark payment as confirmed
		checkout.status = "paid"
		checkout.save()

	# ✅ Create order AFTER releasing lock
	result = create_order_from_cart(session_key, slug)

	if result["success"]:
		print(f"ORDER CREATED: {result['order_id']}")
		return HttpResponse("Payment received", status=200)
	else:
		print("ORDER FAILED:", result["error"])
		return HttpResponse(result["error"], status=500)
	