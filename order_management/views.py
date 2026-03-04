from django.shortcuts import render
from django.shortcuts import render

# order_management/services.py (or utils.py)
from .models import ORDER
from cart_management.models import CART
from django.contrib.auth.models import User

def create_order_from_cart(user, payment_method="card"):
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
            orderStatus="pending"
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
        orders = ORDER.objects.filter(user=user).order_by("-id")

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
    """
    Returns all orders for business dashboard.
    """

    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    orders = ORDER.objects.all().order_by("-id")

    order_list = []

    for order in orders:
        order_list.append({
            "order_id": order.id,
            "user_id": order.user.id,
            "items": order.menuCartItems,
            "status": order.orderStatus,
            "payment_method": order.paymentMethod,
        })

    return JsonResponse({"orders": order_list}, status=200)