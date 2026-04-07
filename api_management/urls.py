from django.urls import path
from . import views

urlpatterns = [
	path('', views.DisplayPage),

	path("api/auth-status", views.AuthStatus.as_view()),
	path("api/login", views.Login.as_view()),
    path("api/refresh", views.Refresh.as_view()),
    path("api/logout", views.Logout.as_view()),

	#USER MANAGEMENT API ENDPOINTS
	path('api/register', views.Register.as_view(), name='api-register'),

	#PRODUCT MANAGEMENT API ENDPOINTS - FOR MENU
	path('api/menu', views.MenuManagement.as_view(), name='api-product-menu'),
	path('<slug:slug>/api/menu', views.MenuManagement.as_view(), name='api-product-menu'),

    path('api/product', views.ProductManagement.as_view(), name='api-product'),
	path('api/product/<int:pk>', views.ProductManagement.as_view(), name='api-product-id'),

	#CART MANAGEMENT ROUTES
	path('<slug:slug>/api/cart', views.CartManagement.as_view(), name='api-cart'),
    path('api/cart', views.CartManagement.as_view(), name='api-cart'),
	path('api/cart/<int:pk>', views.CartManagement.as_view(), name='api-cart-id'),
	path('<slug:slug>/api/cart/<int:pk>', views.CartManagement.as_view(), name='api-cart-id'),
    
	#CHECKOUT MANAGEMENT API ENDPOINTS
	path('api/checkout', views.CheckoutManagement.as_view(), name='api-checkout'),

	#ORDER MANAGEMENT ROUTES
    path('api/orders/all', views.OrderManagement.as_view(), name='api-orders-dashboard'),
	path('api/orders/track', views.TrackOrder.as_view(), name='api-orders-tracking'),
	path('api/orders/<int:pk>', views.OrderManagement.as_view(), name='api-orders-update'),
	path('api/orders/<int:pk>/status', views.OrderManagement.as_view(), name='api-orders-tracking'),

	#USER MANAGEMENT API ENDPOINTS
	path('api/ipn', views.PaymentNotification.as_view(), name='api-payment-notification'),
]
