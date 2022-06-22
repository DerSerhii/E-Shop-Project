from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _

from online_shop import settings


class Customer(AbstractUser):
    wallet = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        ordering = ["username"]

    def __str__(self):
        return self.username


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/")
    amount = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ["name"]

    def __str__(self):
        return self.name[:15]


class Purchase(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    amount = models.PositiveSmallIntegerField()
    time_purchase = models.DateTimeField(auto_now_add=True)
    # price at the time of purchase - ?

    class Meta:
        verbose_name = _("Purchase")
        verbose_name_plural = _("Purchases")
        ordering = ["-time_purchase"]

    def __str__(self):
        return f"Purchase #{self.pk}"


class PurchaseReturns(models.Model):
    to_purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT)
    time_request_return = models.DateTimeField(auto_now_add=True)
    # amount of returned goods - ?

    class Meta:
        verbose_name = _("Purchase returns")
        verbose_name_plural = _("Purchase returns")
        ordering = ["-time_request_return"]

    def __str__(self):
        return f"Return purchase #{self.to_purchase.pk}"
