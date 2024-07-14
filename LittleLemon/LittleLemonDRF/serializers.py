from rest_framework import serializers 
from .models import Rating 
from rest_framework.validators import UniqueTogetherValidator 
#ensures that a combination of fields is unique
from django.contrib.auth.models import User 
from .models import MenuItem, Category, Cart, Order, OrderItem
from decimal import Decimal
 

class GroupUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exist")
        return value
    
    
class RatingSerializer (serializers.ModelSerializer): 
    user = serializers.PrimaryKeyRelatedField( 
    queryset=User.objects.all(), 
    default=serializers.CurrentUserDefault() 
    ) #type of field provided by DRF to handle relationships using primary keys

    class Meta:
        model = Rating
        fields = ['user','menuitem_id','rating']
        validators = UniqueTogetherValidator(queryset=Rating.objects.all(),fields=['user', 'menuitem_id'])
        extra_kwargs = {
           'rating':{
               'max_value':5,
               'min_value':0
           },
        }


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = ['id','title','price','featured','category','category_id']


class CartSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField(method_name='calculate_total')

    class Meta:
        model = Cart
        fields = ['id', 'user', 'menu_item', 'quantity', 'unit_price', 'price']

    def calculate_total(self, cart: Cart):
        return cart.unit_price * cart.quantity
    
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

 
class OrderItemSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menu_item', 'quantity', 'unit_price', 'price']
        read_only_fields = ['order']

    def get_price(self, obj):
        return obj.unit_price * obj.quantity

    def create(self, validated_data):
        order = self.context.get('order')
        validated_data['order'] = order
        return super().create(validated_data)