import warnings

from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DeleteView, CreateView, DetailView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from online_shop import settings
from .forms import RegisterCustomerForm, BuyForm, WalletCustomerForm, AdminProductForm
from .models import Product, Customer, Category, Purchase, PurchaseReturns
from .utils import DataMixin


class ShopHome(DataMixin, ListView):
    model = Product
    template_name = "e_shop/index.html"
    context_object_name = "products"
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # additional context
        title = "Admin-Products" if self.request.user.is_superuser else "E-Shop"
        context_add = self.get_user_context(title=title)
        context.update(context_add)
        return context

    def get_queryset(self):
        return super().get_queryset() \
            if self.request.user.is_superuser \
            else Product.objects.filter(is_available=True)


class ShowProduct(DataMixin, DetailView):
    model = Product
    slug_url_kwarg = 'prod_slug'
    template_name = 'e_shop/product.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        self.extra_context = {'buy_form': BuyForm(self.object)}

        # additional context
        context = super().get_context_data(**kwargs)
        context_add = self.get_user_context(title=context['product'])
        context.update(context_add)
        return context


class BuyView(LoginRequiredMixin, CreateView):
    form_class = BuyForm
    slug_url_kwarg = "prod_slug"
    http_method_names = ["post"]
    success_url = reverse_lazy("home")
    login_url = reverse_lazy("login")

    def get_form_kwargs(self):
        slug = self.kwargs[self.slug_url_kwarg]
        product = Product.objects.get(slug=slug)

        kwargs = super().get_form_kwargs()
        kwargs.update({"product": product})
        return kwargs

    def form_valid(self, form):
        purchase = form.save(commit=False)
        purchase.customer = self.request.user

        # money sufficiency check
        wallet_customer = purchase.customer.wallet
        purchase_total = purchase.price_at_time_purchase * purchase.amount
        if purchase_total > wallet_customer:
            self.request.session["msg_lack_money"] = f"{purchase_total - wallet_customer}"
            return redirect(reverse("wallet", kwargs={"cust_id": purchase.customer.pk}))

        purchase.customer.wallet -= purchase_total
        purchase.product.amount -= purchase.amount

        with transaction.atomic():
            purchase.customer.save()
            purchase.product.save()
            purchase.save()

        return super().form_valid(form=form)


class ShowPurchase(LoginRequiredMixin, DataMixin, ListView):
    model = Purchase
    template_name = "e_shop/purchase.html"
    context_object_name = "purchases"
    login_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # put the refund message in the context
        msg_request_refund = self.request.session.get('msg_request_refund')
        if msg_request_refund:
            context.update({"msg_request_refund": msg_request_refund})
            del self.request.session['msg_request_refund']

        # additional context from the mixin
        context_add = self.get_user_context(title="E-Shop|MyPurchases")
        context.update(context_add)
        return context

    def get_queryset(self):
        return Purchase.objects.filter(customer=self.request.user)


class RefundPurchase(LoginRequiredMixin, DataMixin, SingleObjectMixin, View):
    model = Purchase
    pk_url_kwarg = 'pur_id'
    refund_period = settings.GUARANTEED_REFUND_PERIOD
    login_url = reverse_lazy("login")
    success_url = reverse_lazy("home")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.purchase = None

    def post(self, request, *args, **kwargs):
        self.purchase = self.get_object()
        if not isinstance(self.purchase, Purchase):
            warnings.warn\
                ("For correct operation, the object must have the attributes of the Purchase class")

        if self.check_period_refund():
            PurchaseReturns.objects.get_or_create(to_purchase=self.purchase)
            message = "The refund request has been sent to the store administration"
        else:
            message = "Unfortunately, the refund period has expired"
        self.create_message(message)

        return redirect("purchase")

    def check_period_refund(self):
        current_time = timezone.now()
        time_purchase = self.purchase.time_purchase
        refund_end_time = time_purchase.replace(minute=time_purchase.minute + self.refund_period)
        check = current_time < refund_end_time
        return check

    def create_message(self, message) -> None:
        self.request.session["msg_request_refund"] = [self.purchase.pk, message]


class WalletCustomer(LoginRequiredMixin, UpdateView):
    model = Customer
    pk_url_kwarg = "cust_id"
    form_class = WalletCustomerForm
    template_name = "e_shop/wallet.html"
    login_url = reverse_lazy("login")
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # put lack of money into context
        difference = self.request.session.get('msg_lack_money')
        if difference:
            context.update({"difference": difference})
            del self.request.session['msg_lack_money']
        return super().get_context_data(**context)

    def form_valid(self, form):
        wallet_form = form.save(commit=False)

        # add money to existing
        current_wallet = self.request.user.wallet
        wallet_form.wallet += current_wallet

        with transaction.atomic():
            wallet_form.save()

        return super().form_valid(form=form)


class ProductCategory(DataMixin, ListView):
    model = Product
    template_name = 'e_shop/index.html'
    context_object_name = 'products'

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Product.objects.filter(category__slug=self.kwargs["cat_slug"])
        else:
            queryset = Product.objects.filter(category__slug=self.kwargs["cat_slug"],
                                              is_available=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # additional context
        current_slug = context["view"].kwargs["cat_slug"]
        current_category = Category.objects.get(slug=current_slug)
        context_add = self.get_user_context(title=f"Category-{current_category}",
                                            cat_selected=current_category.id)
        context.update(context_add)
        return context


class RegisterCustomer(DataMixin, CreateView):
    form_class = RegisterCustomerForm
    template_name = 'e_shop/register.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # additional context
        context_add = self.get_user_context(title='Registration')
        context.update(context_add)
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class Login(DataMixin, LoginView):
    form_class = AuthenticationForm
    template_name = 'e_shop/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # additional context
        context_add = self.get_user_context(title='Authorization')
        context.update(context_add)
        return context

    def get_success_url(self):
        return reverse_lazy('home')


class Logout(LogoutView):
    next_page = "home"


class AdminAddProduct(LoginRequiredMixin, UserPassesTestMixin, DataMixin, CreateView):
    form_class = AdminProductForm
    template_name = "e_shop/admin-product.html"
    success_url = reverse_lazy("home")
    login_url = reverse_lazy("login")

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # additional context
        context_add = self.get_user_context(title="Admin-Add Product",
                                            action="Add")
        context.update(context_add)
        return context


class AdminAddCategory(LoginRequiredMixin, UserPassesTestMixin, DataMixin, CreateView):
    model = Category
    fields = "__all__"
    template_name = "e_shop/admin-category.html"
    success_url = reverse_lazy("home")
    login_url = reverse_lazy("login")

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # additional context
        context_add = self.get_user_context(title="Admin-Add Category",
                                            action="Add")
        context.update(context_add)
        return context


class AdminEditProduct(LoginRequiredMixin, UserPassesTestMixin, DataMixin, UpdateView):
    model = Product
    slug_url_kwarg = 'prod_slug'
    form_class = AdminProductForm
    template_name = "e_shop/admin-product.html"
    success_url = reverse_lazy("home")
    login_url = reverse_lazy("login")

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # additional context
        context_add = self.get_user_context(title="Admin-Edit Product",
                                            action="Edit")
        context.update(context_add)
        return context


class AdminEditCategory(LoginRequiredMixin, UserPassesTestMixin, DataMixin, UpdateView):
    model = Category
    fields = "__all__"
    slug_url_kwarg = "cat_slug"
    template_name = "e_shop/admin-category.html"
    success_url = reverse_lazy("home")
    login_url = reverse_lazy("login")

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # additional context
        context_add = self.get_user_context(title="Admin-Edit Category",
                                            action="Edit")
        context.update(context_add)
        return context


class AdminShowRefundPurchase(LoginRequiredMixin, UserPassesTestMixin, DataMixin, ListView):
    model = PurchaseReturns
    template_name = "e_shop/admin-refund.html"
    context_object_name = "refunds"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # additional context from the mixin
        context_add = self.get_user_context(title="Show Refunds")
        context.update(context_add)
        return context


class AdminRemoveRefundPurchase(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PurchaseReturns
    pk_url_kwarg = "ref_id"
    success_url = reverse_lazy("admin-refund")
    login_url = reverse_lazy("login")

    def test_func(self):
        return self.request.user.is_superuser


class AdminApproveRefundPurchase(LoginRequiredMixin, UserPassesTestMixin, SingleObjectMixin, View):
    model = PurchaseReturns
    pk_url_kwarg = 'ref_id'
    login_url = reverse_lazy("login")
    success_url = reverse_lazy("home")

    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request, *args, **kwargs):
        return_purchase = self.get_object()
        if not isinstance(return_purchase, PurchaseReturns):
            warnings.warn\
                ("For correct operation, the object must have the attributes of the PurchaseReturns class")

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

        return redirect("admin-refund")
