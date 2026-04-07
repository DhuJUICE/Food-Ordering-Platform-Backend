from django.http import JsonResponse
from rest_framework.views import APIView
from .models import CART
from product_management.models import PRODUCT
from cart_management.models import CARTITEM
from tenant_management.models import TENANT

from django.db import IntegrityError
from django.forms.models import model_to_dict

class CartManagement(APIView):
	"""Session-based cart API"""

	def _get_cart(self, request, slug=None):
		if not request.session.session_key:
			request.session.create()
	
		session_key = request.session.session_key		
		

		cart, _ = CART.objects.get_or_create(session_key=session_key)
		return cart

	def get(self, request, slug):
		try:
			# Ensure session
			if not request.session.session_key:
				request.session.create()
			session_key = request.session.session_key

			# Try to get tenant
			try:
				tenant = TENANT.objects.get(slug=slug)
			except TENANT.DoesNotExist:
				return JsonResponse({
					"success": False,
					"message": f"No business found with slug '{slug}'"
				}, status=404)  # 404 is appropriate for not found

			# Find the cart for this session + tenant
			cart = CART.objects.filter(session_key=session_key, tenant=tenant).first()

			if not cart:
				return JsonResponse({"success": True, "cartItems": []}, status=200)

			cartitems = CARTITEM.objects.filter(cart=cart).select_related('product')

			items = [
				{
					"id": item.id,
					"product": model_to_dict(item.product),
					"quantity": item.quantity,
				}
				for item in cartitems
			]
			print(items)
			return JsonResponse({"success": True, "cartItems": items}, status=200)

		except Exception as e:
			return JsonResponse({
				"success": False,
				"error": str(e)
			}, status=500)
		
	def post(self, request, slug, pk):
		if not request.session.session_key:
			request.session.create()
		
		session_key = request.session.session_key

		from django.shortcuts import get_object_or_404
		tenant = get_object_or_404(TENANT, slug=slug)

		cart, _ = CART.objects.get_or_create(
			session_key=session_key,
			tenant=tenant
		)

		product = PRODUCT.objects.get(pk=pk, tenant=tenant)

		try:
			cartitem, created = CARTITEM.objects.get_or_create(
				cart=cart,
				product=product
			)

			if not created:
				cartitem.quantity += 1
				cartitem.save()

		except IntegrityError:
			# If duplicate was attempted due to race condition
			cartitem = CARTITEM.objects.get(cart=cart, product=product)
			cartitem.quantity += 1
			cartitem.save()

		return JsonResponse({"success": True}, status=200)



	def put(self, request, slug):
		try:
			data = request.data
			action = data.get("action")
			product_id = str(data.get("product_id"))

			if not action or not product_id:
				return JsonResponse({"success": False, "error": "Action and product_id are required"}, status=400)

			product = PRODUCT.objects.get(pk=product_id)
			tenant = TENANT.objects.get(slug=slug)
			cart = self._get_cart(request, tenant)
			cart_item = CARTITEM.objects.get(cart=cart, product=product)

			if action == "increment":
				cart_item.quantity += 1
			elif action == "decrement":
				cart_item.quantity -= 1
			elif action == "clear":
				CARTITEM.objects.filter(cart=cart).delete()
			else:
				return JsonResponse({"success": False, "error": "Invalid action"}, status=400)

			# Save only if increment/decrement
			if action in ["increment", "decrement"]:
				cart_item.save()

			# Get all cart items for this cart
			cart_items_qs = CARTITEM.objects.filter(cart=cart).select_related("product")

			# Serialize to list of dicts
			if cart_items_qs.exists():
				cart_items = [
					{
						"id": item.id,
						"product": model_to_dict(item.product),
						"quantity": item.quantity,
					}
					for item in cart_items_qs
				]
			else:
				cart_items = []

			return JsonResponse({"success": True, "cartItems": cart_items}, status=200)

		except PRODUCT.DoesNotExist:
			return JsonResponse({"success": False, "error": "Product not found"}, status=404)
		except CARTITEM.DoesNotExist:
			return JsonResponse({"success": False, "error": "Cart item not found"}, status=404)
		except Exception as e:
			return JsonResponse({"success": False, "error": str(e)}, status=500)

