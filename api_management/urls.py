from django.urls import path
from . import views

#token view imports
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
	path('', views.DisplayPage),

	#Used for custom logging users in - No need for the login endpoint and sends back is_staff attribute for Role Based Access Control
	path('api/token', TokenObtainPairView.as_view(), name='token'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token-refresh'),

	#USER MANAGEMENT API ENDPOINTS
	path('api/register', views.Register.as_view(), name='api-register'),

	#PRODUCT MANAGEMENT API ENDPOINTS - FOR MENU
	path('api/menu', views.MenuManagement.as_view(), name='api-product-menu'),
	path('api/menu/<int:pk>', views.MenuManagement.as_view(), name='api-product-menu'),

	path('api/product', views.ProductManagement.as_view(), name='api-product'),
	path('api/product/<int:pk>', views.ProductManagement.as_view(), name='api-product-id'),

	#CART MANAGEMENT ROUTES
	path('api/cart', views.CartManagement.as_view(), name='api-cart'),
	path('api/cart/<int:pk>', views.CartManagement.as_view(), name='api-cart-id'),

	#CHECKOUT MANAGEMENT API ENDPOINTS
	path('api/checkout', views.CheckoutManagement.as_view(), name='api-checkout'),

	#ORDER MANAGEMENT ROUTES
	path('api/orders/all', views.OrderManagement.as_view(), name='api-orders-dashboard'),
	path('api/orders/track/<path:customer_phone>', views.TrackOrder.as_view(), name='api-orders-tracking'),
	path('api/orders/<int:pk>', views.OrderManagement.as_view(), name='api-orders-update'),
	path('api/orders/<int:pk>/status', views.OrderManagement.as_view(), name='api-orders-tracking'),

	#USER MANAGEMENT API ENDPOINTS
	path('api/ipn', views.PaymentNotification.as_view(), name='api-payment-notification'),
]
