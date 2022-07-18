from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, \
    BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from e_shop.API.permissions import IsAdminOrReadOnly, CustomerBuyAndReadOrAdminReadOnly, \
    CustomerRefundAndReadOrAdminRefundAndRead
from e_shop.API.serializers import RegisterSerializer, ProductReadSerializer, \
    ProductWriteSerializer, CategorySerializer, PurchaseReadSerializer, \
    PurchaseWriteSerializer, RefundReadSerializer, RefundWriteSerializer
from e_shop.models import Purchase, Customer, Product, Category, PurchaseReturns


class RegisterView(CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny, )


class LogoutView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)

        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LogoutAllView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)


class ProductAPIListPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 2


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = ProductAPIListPagination

    def get_queryset(self):
        return super().get_queryset() \
            if self.request.user.is_superuser \
            else Product.objects.filter(is_available=True)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductReadSerializer
        return ProductWriteSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminUser,)
    pagination_class = ProductAPIListPagination


class PurchaseViewSet(ModelViewSet):
    http_method_names = ["get", "post"]
    queryset = Purchase.objects.all()
    permission_classes = (CustomerBuyAndReadOrAdminReadOnly, )
    pagination_class = ProductAPIListPagination

    def get_queryset(self):
        return super().get_queryset() \
            if self.request.user.is_superuser \
            else Purchase.objects.filter(customer=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PurchaseReadSerializer
        if self.request.method == "POST":
            return PurchaseWriteSerializer

    def perform_create(self, serializer):
        customer = serializer.validated_data["customer"]
        product = serializer.validated_data["product"]
        amount_product = serializer.validated_data["amount"]

        price_at_time_purchase = product.price
        purchase_total = amount_product * price_at_time_purchase

        # the current state of the buyer's account
        wallet = customer.wallet

        # the current quantity of the product in stock
        product_amount = product.amount

        wallet -= purchase_total
        customer.wallet = wallet

        product_amount -= amount_product
        product.amount = product_amount

        with transaction.atomic():
            customer.save()
            product.save()
            serializer.save(price_at_time_purchase=price_at_time_purchase)


class RefundPurchaseViewSet(ModelViewSet):
    queryset = PurchaseReturns.objects.all()
    permission_classes = (CustomerRefundAndReadOrAdminRefundAndRead, )
    pagination_class = ProductAPIListPagination

    def get_queryset(self):
        return super().get_queryset() \
            if self.request.user.is_superuser \
            else PurchaseReturns.objects.filter(to_purchase__customer=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RefundReadSerializer
        return RefundWriteSerializer

    @action(detail=True, methods=['delete'])
    def confirm(self, request, pk=None):
        return_purchase = self.get_object()

        # data of the deleted purchase
        purchase = return_purchase.to_purchase
        product = purchase.product
        amount_product = purchase.amount
        price_product = purchase.price_at_time_purchase
        sum_purchase = amount_product * price_product
        customer = purchase.customer

        # the current state of the buyer's account
        wallet = customer.wallet

        # the current quantity of the product in stock
        product_amount = product.amount

        # return data
        wallet += sum_purchase
        customer.wallet = wallet

        product_amount += amount_product
        product.amount = product_amount

        # refund transaction
        with transaction.atomic():
            customer.save()
            product.save()
            return_purchase.delete()
            purchase.delete()

        return Response(status=status.HTTP_207_MULTI_STATUS)
