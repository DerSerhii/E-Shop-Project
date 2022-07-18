from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.validators import UniqueValidator

from e_shop.models import Product, Customer, Purchase, Category, PurchaseReturns


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,
                                     required=True,
                                     validators=[validate_password])
    password2 = serializers.CharField(write_only=True,
                                      required=True)

    class Meta:
        model = Customer
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email',
                  'password',
                  'password2',
                  'wallet')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.\
                ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        customer = Customer(**validated_data)
        customer.set_password(password)
        customer.save()
        return customer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class CategoryPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", )


class ProductReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Product
        exclude = ("slug", )


class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ProductPurchaseSerializer(serializers.ModelSerializer):
    category = CategoryPurchaseSerializer()

    class Meta:
        model = Product
        fields = ("name", "category")


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("username", )


class PurchaseReadSerializer(serializers.ModelSerializer):
    product = ProductPurchaseSerializer()

    class Meta:
        model = Purchase
        fields = "__all__"


class PurchaseWriteSerializer(serializers.ModelSerializer):
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Purchase
        fields = ("id", "customer", "product", "amount")

    def validate(self, data):
        wallet_customer = data["customer"].wallet
        purchase_total = data["product"].price * data["amount"]

        quantity_in_stock = data["product"].amount
        quantity_in_order = data["amount"]

        if purchase_total > wallet_customer:
            raise serializers.ValidationError("Insufficient funds to pay")

        if quantity_in_order > quantity_in_stock:
            raise serializers.ValidationError("This quantity is out of stock")

        return data


class RefundReadSerializer(serializers.ModelSerializer):
    to_purchase = PurchaseReadSerializer()

    class Meta:
        model = PurchaseReturns
        fields = "__all__"


class RefundWriteSerializer(serializers.ModelSerializer):
    to_purchase = PrimaryKeyRelatedField(
        queryset=Purchase.objects.all(),
        validators=[UniqueValidator(queryset=PurchaseReturns.objects.all())])

    class Meta:
        model = PurchaseReturns
        fields = "__all__"
