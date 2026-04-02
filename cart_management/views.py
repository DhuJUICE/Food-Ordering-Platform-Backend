from django.http import JsonResponse
from rest_framework.views import APIView
from .models import CART
from product_management.models import PRODUCT

class CartManagement(APIView):
	"""Session-based cart API"""

	def _get_cart(self, request, tenant=None):
		if not request.session.session_key:
			request.session.create()
		
		session_key = request.session.session_key

		if tenant:
			cart, _ = CART.objects.get_or_create(session_key=session_key, tenant=tenant)
		else:
			cart, _ = CART.objects.get_or_create(session_key=session_key)

		return cart

	def get(self, request):
		try:
			cart = self._get_cart(request)
			return JsonResponse({"success": True, "cart": cart.menuCartItems or {}}, status=200)
		except Exception as e:
			return JsonResponse({"success": False, "error": str(e)}, status=500)

	def put(self, request):
		try:
			data = request.data
			action = data.get("action")
			product_id = str(data.get("productId", ""))

			if not action or (action != "clear" and not product_id):
				return JsonResponse({"success": False, "error": "Action and productId are required"}, status=400)

			product = PRODUCT.objects.get(pk=product_id)

			tenant = product.tenant

			cart = self._get_cart(request, tenant)

			cart_items = cart.menuCartItems or {}

			if action == "add":
				quantity = int(data.get("quantity", 1))
				prod_name = data.get("prodName")
				prod_price = data.get("prodPrice")
				prod_image = data.get("prodImagePath")

				try:
					product = PRODUCT.objects.get(id=product_id)
				except PRODUCT.DoesNotExist:
					return JsonResponse({"success": False, "error": "Product not found"}, status=404)

				# Tenant check
				if cart.tenant and cart.tenant != product.tenant:
					return JsonResponse({"success": False, "error": "Cannot mix products from different tenants"}, status=400)
				elif not cart.tenant:
					cart.tenant = product.tenant  # assign tenant if cart has none


				if not all([prod_name, prod_price, prod_image]):
					return JsonResponse({"success": False, "error": "Product name, price, and image required"}, status=400)

				cart_items[product_id] = {
					"id": product_id,
					"prodName": prod_name,
					"prodPrice": prod_price,
					"prodImagePath": prod_image,
					"quantity": quantity
				}

			elif action == "remove":
				cart_items.pop(product_id, None)

			elif action == "increment":
				if product_id in cart_items:
					cart_items[product_id]["quantity"] = int(cart_items[product_id].get("quantity", 0)) + 1

			elif action == "decrement":
				if product_id in cart_items:
					cart_items[product_id]["quantity"] = max(int(cart_items[product_id].get("quantity", 1)) - 1, 1)

			elif action == "clear":
				cart_items = {}

			else:
				return JsonResponse({"success": False, "error": "Invalid action"}, status=400)

			try:
				cart.menuCartItems = cart_items
				cart.save()
			except Exception as e:
				return JsonResponse({"success": False, "error": f"Failed saving cart: {str(e)}"}, status=500)

			return JsonResponse({"success": True, "cart": cart_items}, status=200)

		except Exception as e:
			return JsonResponse({"success": False, "error": str(e)}, status=500)