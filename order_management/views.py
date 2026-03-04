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
        ##cart.menuCartItems = {}
        ##cart.save()

        return order

    except CART.DoesNotExist:
        return None