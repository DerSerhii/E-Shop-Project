from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
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

    # def get_absolute_url(self):
    #     return reverse("customer", kwargs={"cust_id": self.id})


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True, verbose_name=_("Name of product"))
    slug = models.SlugField(max_length=100, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name=_("Description"))
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name=_("Price"))
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", verbose_name=_("Photo"))
    amount = models.PositiveSmallIntegerField(verbose_name=_("Quantity in stock"))
    category = models.ForeignKey("Category", on_delete=models.PROTECT, verbose_name=_("Product category"))
    is_available = models.BooleanField(default=True, verbose_name=_("Available"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ["name"]

    def __str__(self):
        return self.name[:30]

    def get_absolute_url(self):
        return reverse("product", kwargs={"prod_slug": self.slug})


class Purchase(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    amount = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),
                                                          MaxValueValidator(1000)])
    time_purchase = models.DateTimeField(auto_now_add=True)
    price_at_time_purchase = models.DecimalField(max_digits=9, decimal_places=2)

    class Meta:
        verbose_name = _("Purchase")
        verbose_name_plural = _("Purchases")
        ordering = ["-time_purchase"]

    def __str__(self):
        return f"Invoice #{self.pk}"


class PurchaseReturns(models.Model):
    to_purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT)
    time_request_return = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Purchase returns")
        verbose_name_plural = _("Purchase returns")
        ordering = ["-time_request_return"]

    def __str__(self):
        return f"Return invoice #{self.to_purchase.pk}"


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True, verbose_name=_("Product category"))
    slug = models.SlugField(max_length=100, unique=True, db_index=True, verbose_name="URL")

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["id"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category", kwargs={"cat_slug": self.slug})
