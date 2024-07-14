from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'groups/(?P<group_name>[^/.]+)/users', views.GroupUserViewSet, basename='group-users')

urlpatterns = [
    path('category/', views.CategoryView.as_view(), name='category-list'),
    path('menu-items/', views.MenuItemsView.as_view(), name='menu-item-list'),
    path('menu-items/<int:pk>/', views.SingleMenuItemView.as_view(), name='menu-item-detail'),
    path('cart/menu-items/', views.CartView.as_view(), name='cart-list'),
    path('cart/menu-items/<int:pk>/', views.SingleCartView.as_view(), name='cart-detail'),
    path('orders/', views.OrderItemView.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.SingleOrderItemView.as_view(), name='order-detail'),
    path('groups/<str:group_name>/users/', views.GroupUserViewSet.as_view({'get': 'list_users'}), name='group-user-list'),
    path('groups/<str:group_name>/users/', views.GroupUserViewSet.as_view({'post': 'add_user'}), name='group-user-add'),
    path('groups/<str:group_name>/users/<int:pk>/', views.GroupUserViewSet.as_view({'post': 'remove_user'}), name='group-user-remove'),
]

urlpatterns += router.urls