from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from tenant_management.models import TENANT
from .models import ORDER, ORDERITEM
from cart_management.models import CART, CARTITEM
from django.contrib.auth.models import User
from checkout_management.models import CHECKOUT

from rest_framework import status
from django.db import transaction
from django.forms.models import model_to_dict

from django.db import transaction

def create_order_from_cart(session_key, slug):
	try:
		tenant = TENANT.objects.get(slug=slug)
	except TENANT.DoesNotExist:
		return {
			"success": False,
			"error": "Tenant not found"
		}

	try:
		checkout = CHECKOUT.objects.get(session_key=session_key, tenant=tenant)
	except CHECKOUT.DoesNotExist:
		return {
			"success": False,
			"error": "Checkout not found"
		}

	cart = CART.objects.filter(
		session_key=session_key,
		tenant=tenant
	).first()

	if not cart:
		return {
			"success": False,
			"error": "Cart not found"
		}

	cart_items = CARTITEM.objects.filter(cart=cart).select_related('product')

	if not cart_items.exists():
		return {
			"success": False,
			"error": "Cart is empty"
		}

	try:
		with transaction.atomic():

			# 🔒 Prevent duplicate orders (REAL check)
			existing_order = ORDER.objects.filter(
				tenant=tenant,
				customer_phone=checkout.customer_phone,
				total_amount=checkout.total_amount
			).exists()

			if existing_order:
				return {
					"success": False,
					"error": "Order already exists"
				}

			# ✅ Create order
			order = ORDER.objects.create(
				session_key=session_key,
				tenant=tenant,
				customer_name=checkout.customer_name,
				customer_phone=checkout.customer_phone,
				total_amount=checkout.total_amount,
			)

			# ✅ Create order items
			order_items = [
				ORDERITEM(
					order=order,
					product=item.product,
					quantity=item.quantity,
					price_at_purchase=item.product.price
				)
				for item in cart_items
			]
			ORDERITEM.objects.bulk_create(order_items)

			# ✅ Cleanup
			cart.delete()
			checkout.delete()

		print("Order created successfully!")

		return {
			"success": True,
			"order_id": order.id
		}

	except Exception as e:
		print("ORDER ERROR:", str(e))
		return {
			"success": False,
			"error": str(e)
		}

#allow users to track their order status/progress
def get_user_orders(request, slug):
	if request.method != "GET":
		return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

	session_key = request.session.session_key

	if not session_key:
		return JsonResponse({"success": False, "error": "Customer not identified - no session_key"}, status=400)
	try:
		tenant = TENANT.objects.get(slug=slug)
	except TENANT.DoesNotExist:
		return JsonResponse({"success": False, "error": "Tenant not found"}, status=404)

	# Get all orders for this customer and tenant
	orders = ORDER.objects.filter(session_key=session_key, tenant=tenant).order_by("-id")

	order_items = []

	for order in orders:
		# Get all items for this order
		items_qs = ORDERITEM.objects.filter(order=order).select_related("product")
		items = [
			{
				"product": model_to_dict(item.product),
				"quantity": item.quantity,
				"price_at_purchase": float(item.price_at_purchase),
			}
			for item in items_qs
		]

		order_items.append({
			"order_id": order.id,
			"order_number": order.order_number,
			"items": items,
			"status": order.status,
			"payment_method": order.paymentMethod,
			"total_amount": float(order.total_amount),
			"created_at": order.created_at.isoformat(),
			"updated_at": order.updated_at.isoformat(),
			"is_collected": order.is_collected,
		})

	return JsonResponse({"success": True, "order_items": order_items}, status=200)

def get_all_orders(request):
	if request.method != "GET":
		return JsonResponse({"error": "Invalid request method"}, status=405)

	# Only show orders that are NOT collected and for the logged in associated tenant
	tenant = request.user.userprofile.tenant
	orders = ORDER.objects.filter(is_collected=False, tenant=tenant).order_by("-id")

	order_items = []

	for order in orders:
		# Get all items for this order
		items_qs = ORDERITEM.objects.filter(order=order).select_related("product")
		items = [
			{
				"product": model_to_dict(item.product),
				"quantity": item.quantity,
				"price_at_purchase": float(item.price_at_purchase),
			}
			for item in items_qs
		]

		order_items.append({
			"order_id": order.id,
			"order_number": order.order_number,
			"items": items,
			"status": order.status,
			"payment_method": order.paymentMethod,
			"total_amount": float(order.total_amount),
			"created_at": order.created_at.isoformat(),
			"updated_at": order.updated_at.isoformat(),
			"is_collected": order.is_collected,
		})

	return JsonResponse({"order_items": order_items}, status=200)

def update_orders(request, pk):
	if not pk:
		return JsonResponse({"detail": "Order ID required"}, status=status.HTTP_400_BAD_REQUEST)
	
	try:
		tenant = request.user.userprofile.tenant
		order = ORDER.objects.get(pk=pk, tenant=tenant)
	except ORDER.DoesNotExist:
		return JsonResponse({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

	# Update status if provided
	status_val = request.data.get("status")
	if status_val:
		order.status = status_val

	is_collected = request.data.get("is_collected")

	# Update collected if the user collected their order
	if is_collected:
		order.is_collected = True

	order.save()


	return JsonResponse({
		"order_id": order.id,
		"status": order.status,
		"is_collected": order.is_collected
	}, status=status.HTTP_200_OK)