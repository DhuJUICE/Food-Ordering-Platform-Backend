from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
# order_management/services.py (or utils.py)
from .models import ORDER
from cart_management.models import CART
from django.contrib.auth.models import User
from rest_framework import status

def create_order_from_cart(session_key, customer_name, customer_phone, payment_method="card"):
    try:
        cart = CART.objects.get(session_key=session_key)

        if not cart.menuCartItems:
            return None

        order = ORDER.objects.create(
            menuCartItems=cart.menuCartItems,
            paymentMethod=payment_method,
            orderStatus="pending",
            customer_name = customer_name,
            customer_phone = customer_phone
        )

        # Clear the cart after saving
        cart.menuCartItems = {}
        cart.save()

        return order

    except CART.DoesNotExist:
        return None

#allow users to track their order status/progress
def get_user_orders(request, customer_phone):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        orders = ORDER.objects.filter(customer_phone=customer_phone, collected=False).order_by("-id")

        order_list = []

        for order in orders:
            order_list.append({
                "order_id": order.id,
                "items": order.menuCartItems,
                "status": order.orderStatus,
                "payment_method": order.paymentMethod,
            })

        return JsonResponse({"orders": order_list}, status=200)

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

def get_all_orders(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    # Only show orders that are NOT collected
    orders = ORDER.objects.filter(collected=False).order_by("-id")

    order_list = []
    for order in orders:
        order_list.append({
            "order_id": order.id,
            "items": order.menuCartItems,
            "status": order.orderStatus,
            "payment_method": order.paymentMethod,
            "collected": order.collected,
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone,
        })

    return JsonResponse({"orders": order_list}, status=200)

def update_orders(request, pk):
	if not pk:
		return JsonResponse({"detail": "Order ID required"}, status=status.HTTP_400_BAD_REQUEST)
	
	try:
		order = ORDER.objects.get(id=pk)
	except ORDER.DoesNotExist:
		return JsonResponse({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

	# Update status if provided
	status_val = request.data.get("status")
	if status_val:
		order.orderStatus = status_val

	if not request.session.session_key:
		request.session.create()
	session_key = request.session.session_key

	# Update collected if provided
	if request.data.get("collected") is True:
		order.collected = True
		cart = CART.objects.get(session_key=session_key)
		cart.delete()

	order.save()
	return JsonResponse({
		"order_id": order.id,
		"status": order.orderStatus,
		"collected": order.collected
	}, status=status.HTTP_200_OK)