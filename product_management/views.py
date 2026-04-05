from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import PRODUCT
from api_management.serializers import ProductSerializer
from django.shortcuts import get_object_or_404
from tenant_management.models import TENANT

class MenuManagement(APIView):
    def get(self, request, slug, pk=None):

        tenant = get_object_or_404(TENANT, slug=slug)
        
        products = PRODUCT.objects.filter(is_available=True, tenant=tenant)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductManagement(APIView):
    def get(self, request, pk=None):
        tenant = request.user.userprofile.tenant
        if pk:
            try:
                product = PRODUCT.objects.get(pk=pk, tenant=tenant)
                serializer = ProductSerializer(product)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except PRODUCT.DoesNotExist:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            products = PRODUCT.objects.filter(tenant=tenant)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            print(serializer.data)

    def post(self, request):
        data = request.data.copy()

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            tenant = request.user.userprofile.tenant
            if tenant:
                serializer.save(    
                    user=request.user,
                    tenant=tenant
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            tenant = request.user.userprofile.tenant
            product = PRODUCT.objects.get(pk=pk, tenant=tenant)
        except PRODUCT.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            tenant = request.user.userprofile.tenant
            
            product = PRODUCT.objects.get(pk=pk, tenant=tenant)
            product.delete()
            return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except PRODUCT.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)