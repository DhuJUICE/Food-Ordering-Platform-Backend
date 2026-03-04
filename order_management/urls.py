from django.urls import path
from .views import *
urlpatterns = [
	path('orders/<int:user_id>', get_user_orders, name='get-user-orders'),
	path('orders/all', get_all_orders, name='get-all-orders'),
]

