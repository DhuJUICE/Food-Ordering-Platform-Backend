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
from auth_management.views import *

#AUTHENTICATION ENDPOINT
class AuthStatus(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return auth_status(request)

class Login(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		return login_view(request)
	
class Refresh(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		return refresh_view(request) 

class Logout(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		return logout_view(request) 

# Basic page view for default backend landing page
def DisplayPage(request):
    return render(request, 'api_template.html')

#PAYMENT NOTIFICATION ENDPOINT
class PaymentNotification(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Delegate directly to the core payment notification and order creation
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

    def get(self, request, pk=None, tenant_slug=None):
        return PMView().get(request, pk=pk, tenant_slug=tenant_slug)

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

#TRACK ORDER MANAGEMENT ENDPOINT
class TrackOrder(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return get_user_orders(request)

#ORDER MANAGEMENT ENDPOINT
class OrderManagement(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        return get_all_orders(request)
            
    def put(self, request, pk=None):
        return update_orders(request, pk)

    def delete(self, request, pk=None):
        return Response({"detail": "Not implemented yet."}, status=status.HTTP_501_NOT_IMPLEMENTED)
