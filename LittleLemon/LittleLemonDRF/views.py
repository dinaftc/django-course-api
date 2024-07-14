from rest_framework import viewsets,generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Rating, Cart, Order, OrderItem
from .serializers import RatingSerializer,GroupUserSerializer
from django.contrib.auth.models import User, Group
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .models import MenuItem, Category
from datetime import datetime
from .permissions import  IsManager, IsDeliveryBoy,IsSuperAdminOrManagerOrReadOnly 
from .serializers import MenuItemSerializer, CategorySerializer,CartSerializer,OrderItemSerializer,OrderSerializer


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields=['title','price','featured']
    permission_classes = [IsAuthenticated]


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminOrManagerOrReadOnly]

class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields=['title']
    permission_classes = [IsAuthenticated]

class SingleCategoryView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsSuperAdminOrManagerOrReadOnly]

class CartView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated,]

class SingleCartView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated ,IsDeliveryBoy]

class OrderView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    search_fields=['staus','date']
    permission_classes = [IsAuthenticated]

class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
class OrderItemView(generics.ListCreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
   

    def create(self, request, *args, **kwargs):
        user = User.objects.get(id=1)  # Get the current user

        # Retrieve current cart items for the user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"error": "No items in the cart to create an order"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total price from cart items
        total_price = sum(item.unit_price * item.quantity for item in cart_items)

        # Create order
        order_data = {
            'user': user.id,
            'status': False,  # Assuming False means not delivered
            'total': total_price,
            'date': datetime.now().date(),
        }

        order_serializer = OrderSerializer(data=order_data)
        if order_serializer.is_valid():
            order = order_serializer.save()

            # Create order items from cart items
            order_items_data = []
            for cart_item in cart_items:
                order_items_data.append({
                    'menu_item': cart_item.menu_item.id,
                    'quantity': cart_item.quantity,
                    'unit_price': cart_item.unit_price,
                    'price': cart_item.unit_price * cart_item.quantity,
                })

            order_item_serializer = OrderItemSerializer(data=order_items_data, many=True, context={'order': order})
            if order_item_serializer.is_valid():
                order_item_serializer.save()

                # Delete all cart items for this user
                cart_items.delete()

                # Custom response data
                response_data = {
                    'items': order_item_serializer.data,
                    'total_price': total_price
                }

                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                order.delete()  # Rollback order creation if order items creation fails
                return Response(order_item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class SingleOrderItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

class GroupUserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, ]

    def get_group(self, group_name):
        return get_object_or_404(Group, name=group_name)

    @action(detail=False, methods=['get'], url_path='list_users')
    def list_users(self, request, *args, **kwargs):
        group_name = self.kwargs.get('group_name')
        print(group_name)
        group = self.get_group(group_name)
        print(group)
        users = group.user_set.all()
        user_data = [{'id': user.id, 'username': user.username} for user in users]
        return Response(user_data)

    @action(detail=False, methods=['post'], url_path='add_user')
    def add_user(self, request, *args, **kwargs):
        group_name = kwargs.get('group_name')
        serializer = GroupUserSerializer(data=request.data)
        if serializer.is_valid():
            group = self.get_group(group_name)
            user = User.objects.get(id=serializer.validated_data['user_id'])
            group.user_set.add(user)
            return Response({'status': 'user added'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='remove_user')
    def remove_user(self, request, *args, **kwargs):
        group_name = kwargs.get('group_name')
        serializer = GroupUserSerializer(data=request.data)
        if serializer.is_valid():
            group = self.get_group(group_name)
            user = User.objects.get(id=serializer.validated_data['user_id'])
            group.user_set.remove(user)
            return Response({'status': 'user removed'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)