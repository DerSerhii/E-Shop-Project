from rest_framework import serializers

from e_shop.models import Product, Customer, Purchase, Category

CEFR_CHOICES = (
    ("A1", "Beginner"),
    ("A2", "Elementary"),
    ("B1", "Intermediate"),
    ("B2", "Upper-Intermediate"),
    ("C1", "Advanced"),
    ("C2", "Proficiency")
)

SEX_CHOICES = (
    ("M", "Male"),
    ("F", "Female")
)


class CandidateCefrSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=30, min_length=2)
    sex = serializers.ChoiceField(choices=SEX_CHOICES)
    age = serializers.IntegerField(min_value=16)
    eng_level = serializers.ChoiceField(choices=CEFR_CHOICES)
    
    def validate(self, data):
        validated_data = super().validate(data)
        sex = validated_data.get("sex")
        age = validated_data.get("age")
        eng_level = validated_data.get("eng_level")
        
        admission_male = sex == "M" and age >= 20 and eng_level in ["C1", "C2"]
        admission_female = sex == "F" and age > 22 and eng_level in ["B2", "C1", "C2"]
        
        if not (admission_male or admission_female):
            raise serializers.ValidationError \
                ("Sorry, your questionnaire does not match the search criteria")
        return data


# from e_shop.API.serializers import CandidateCefrSerializer
# import io
# from rest_framework.parsers import JSONParser
# stream = io.BytesIO(b'{"name": "Alex", "sex": "M", "age": "27", "eng_level": "C1"}')
# data = JSONParser().parse(stream)
# serializer = CandidateCefrSerializer(data=data)
# serializer.is_valid(raise_exception=True)
# serializer.validated_data


class CustomerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Customer
        fields = ["username", "first_name", "last_name", "email", "password", "wallet"]

    def create(self, validated_data):
        customer = Customer(**validated_data)
        customer.set_password(validated_data["password"])
        customer.save()
        return customer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class PurchaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    time_purchase = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Purchase
        fields = '__all__'

# from e_shop.API.serializers import CustomerSerializer, PurchaseSerializer, ProductSerializer, CategorySerializer
# from e_shop.models import Customer, Purchase, Product, Category
#
# data = {'username': 'Django', 'password': 'django123', 'wallet': 10000.00}
# customer = CustomerSerializer(data=data)
# customer.is_valid(raise_exception=True)
# customer.save()
#
# data = {'name': 'Securities', 'slug': 'securities'}
# category = CategorySerializer(data=data)
# category.is_valid(raise_exception=True)
# category.save()
#
# category_id = Category.objects.get(name='Securities').id
# data = {'name': 'Certificate of unchained', 'slug': 'cert-unchained', 'price': 10000.00, 'amount': 1, 'category': category_id}
# product = ProductSerializer(data=data)
# product.is_valid(raise_exception=True)
# product.save()
#
# customer_id = Customer.objects.get(username='Django').id
# product_id = Product.objects.get(name='Certificate of unchained').id
# data = {'customer': customer_id, 'product': product_id, 'amount': 1, 'price_at_time_purchase': 10000.00}
# purchase = PurchaseSerializer(data=data)
# purchase.is_valid(raise_exception=True)
# purchase.save()
#
# cust = Customer.objects.get(username='Django')
# cust_ser = CustomerSerializer(cust)
# cust_ser.data
#
# prod = Product.objects.get(name='Certificate of unchained')
# prod_ser = ProductSerializer(prod)
# prod_ser.data
#
# pur = Purchase.objects.first()
# pur_ser = PurchaseSerializer(pur)
# pur_ser.data
