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
from product_management.views import ProductManagement as PMView, MenuManagement as MMView
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

    def get(self, request, pk=None):
        slug = request.session.get("slug")
        return MMView().get(request, slug, pk=pk)

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

    def get(self, request, slug=None):
        if not request.session.get("slug"):
            if not slug:
                return JsonResponse({"success": False, "error": "Tenant slug missing"}, status=400)
            request.session["slug"] = slug
        else:
            slug = request.session.get("slug")
        return CartMainView().get(request, slug)

    def post(self, request, pk):
        slug = request.session.get("slug")
        return CartMainView().post(request, pk, slug)
    
    def put(self, request):
        return CartMainView().put(request)

    def delete(self, request, pk):
        slug = request.session.get("slug")
        try:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key

            tenant = get_object_or_404(TENANT, slug=slug)
            cart = get_object_or_404(CART, session_key=session_key, tenant=tenant)

            if not pk:
                return JsonResponse({"success": False, "message": "productId is required"}, status=400)

            cartitem = get_object_or_404(CARTITEM, cart=cart, product_id=pk)

            cartitem.delete()

            return JsonResponse({"success": True, "message": "Cart item removed successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

# CHECKOUT MANAGEMENT ENDPOINT
class CheckoutManagement(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return checkout(request)

#TRACK ORDER MANAGEMENT ENDPOINT
class TrackOrder(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        slug = request.session.get("slug")
        return get_user_orders(request, slug)

#ORDER MANAGEMENT ENDPOINT
class OrderManagement(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        return get_all_orders(request)
            
    def put(self, request, pk=None):
        return update_orders(request, pk)

    def delete(self, request, pk=None):
        return Response({"detail": "Not implemented yet."}, status=status.HTTP_501_NOT_IMPLEMENTED)
