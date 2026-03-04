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

# Basic page view for default backend landing page
def DisplayPage(request):
    return render(request, 'api_template.html')

#Account creation endpoint
class Register(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Delegate directly to the core register view
        return register_view(request)

#Menu display management endpoint
class MenuManagement(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        return PMView().get(request, pk=pk)

#Menu management endpoint
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

# Single cart endpoint through API
class CartManagement(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return CartMainView().get(request)

    def put(self, request):
        return CartMainView().put(request)

# CHECKOUT MANAGEMENT API ENDPOINTS
class CheckoutManagement(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return checkout(request)
