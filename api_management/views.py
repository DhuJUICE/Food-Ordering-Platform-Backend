from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now as timezone_now
from django.contrib.auth.models import User
import json

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response

from .serializers import *

from checkout_management.views import checkout
from user_management.views import *
from product_management.views import ProductManagement as PMView
from checkout_management.views import *
from cart_management.views import CartManagement as CartMainView
from order_management.views import *

# Basic page view for default backend landing page
def DisplayPage(request):
    return render(request, 'api_template.html')

#PAYMENT NOTIFICATION ENDPOINT
class PaymentNotification(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Delegate directly to the core register view
        return payfast_ipn(request)

#ACCOUNT CREATION ENDPOINT
class Register(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Delegate directly to the core register view
        return register_view(request)

#MENU DISPLAY MANAGEMENT ENDPOINT
class MenuManagement(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        return PMView().get(request, pk=pk)

#MENU MANAGEMENT ENDPOINT
class ProductManagement(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        return PMView().get(request, pk=pk)

    def post(self, request):
        return PMView().post(request)

    def put(self, request, pk=None):
        return PMView().put(request, pk=pk)

    def delete(self, request, pk=None):
        return PMView().delete(request, pk=pk)

# CART MANAGEMENT ENDPOINT
class CartManagement(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return CartMainView().get(request)

    def put(self, request):
        return CartMainView().put(request)

# CHECKOUT MANAGEMENT ENDPOINT
class CheckoutManagement(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return checkout(request)

#ORDER MANAGEMENT ENDPOINT
class TrackOrder(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        """
        If user_id is provided: fetch orders for that user (Track Order)
        Otherwise: fetch all orders (Business Dashboard)
        """
        if pk:
            # Redirect to your core function
            return get_user_orders(request, pk)

class OrderManagement(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        return get_all_orders(request)
            
    def put(self, request, pk=None):
            if not pk:
                return Response({"detail": "Order ID required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                order = ORDER.objects.get(id=pk)
            except ORDER.DoesNotExist:
                return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

            # Update status if provided
            status_val = request.data.get("status")
            if status_val:
                order.orderStatus = status_val

            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            print(session_key)
            # Update collected if provided
            if request.data.get("collected") is True:
                order.collected = True
                cart = CART.objects.get(session_key=session_key)
                cart.delete()

            order.save()
            return Response({
                "order_id": order.id,
                "status": order.orderStatus,
                "collected": order.collected
            }, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete an order.
        """
        return Response({"detail": "Not implemented yet."}, status=status.HTTP_501_NOT_IMPLEMENTED)
