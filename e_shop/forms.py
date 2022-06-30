from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import ValidationError

from .models import Customer, Purchase, Product, Category


class RegisterCustomerForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = ("username", "first_name", "last_name", "email",
                  "password1", "password2", "wallet")

    def clean_wallet(self):
        wallet = self.cleaned_data.get("wallet")
        if wallet < 0:
            raise ValidationError("The field can't be negative")
        return wallet


class WalletCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("wallet", )
        labels = {"wallet": "Top up your account: "}

    def clean_wallet(self):
        wallet = self.cleaned_data.get("wallet")
        if wallet < 0:
            raise ValidationError("Attention! You want to replenish your wallet, not to lose money)"
                                  " Use positive numbers")
        return wallet


class BuyForm(forms.ModelForm):
    def __init__(self, product=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product
        self.fields['amount'].widget.attrs["min"] = 1
        self.fields['amount'].widget.attrs["max"] = self.product.amount

    class Meta:
        model = Purchase
        fields = ("amount",)
        labels = {"amount": "Order quantity: "}

    def save(self, commit=True):
        form = super().save(commit=False)
        form.product = self.product
        form.price_at_time_purchase = self.product.price
        if commit:
            form.save()
        return form


class AdminProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price <= 0:
            raise ValidationError("The price can't be negative and is equal to zero")
        return price
