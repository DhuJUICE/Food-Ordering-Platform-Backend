from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
# order_management/services.py (or utils.py)
from .models import ORDER
from cart_management.models import CART
from django.contrib.auth.models import User

def create_order_from_cart(user, customer_name, customer_phone, customer_email, payment_method="card"):
    """
    Create a new ORDER from the user's current cart.
    Clears the cart after saving.
    """
    try:
        cart = CART.objects.get(user=user)
        if not cart.menuCartItems:
            return None

        order = ORDER.objects.create(
            user=user,
            menuCartItems=cart.menuCartItems,
            paymentMethod=payment_method,
            orderStatus="pending",
            customer_name = customer_name,
            customer_phone = customer_phone,
            customer_email = customer_email
        )

        # Clear the cart after saving
        cart.menuCartItems = {}
        cart.save()

        return order

    except CART.DoesNotExist:
        return None


#allow users to track their order status/progress
def get_user_orders(request, user_id):
    """
    Returns all orders for a specific user.
    Used for Track Order page.
    """

    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        user = User.objects.get(id=user_id)
        orders = ORDER.objects.filter(user=user, collected=False).order_by("-id")

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
            "user_id": order.user.id,
            "items": order.menuCartItems,
            "status": order.orderStatus,
            "payment_method": order.paymentMethod,
            "collected": order.collected,
        })

    return JsonResponse({"orders": order_list}, status=200)

def update_order_status(order_id, new_status):
    """
    Update the status of an order.
    Returns the updated order as a dict or None if invalid.
    """
    valid_statuses = ["pending", "preparing", "done", "cancelled"]

    if new_status not in valid_statuses:
        return None

    try:
        order = ORDER.objects.get(id=order_id)
        order.orderStatus = new_status
        order.save()

        return {
            "order_id": order.id,
            "user_id": order.user.id,
            "items": order.menuCartItems,
            "status": order.orderStatus,
            "payment_method": order.paymentMethod,
        }
    except ORDER.DoesNotExist:
        return None