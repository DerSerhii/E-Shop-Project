from django.contrib import admin

from e_shop.models import Customer, Product, Purchase, PurchaseReturns, Category


class CustomerAdmin(admin.ModelAdmin):
    list_display = ("username", "wallet", "first_name", "last_name", "email", "is_staff")
    list_display_links = ("username",)
    search_fields = ("username", "first_name", "last_name", "email")


class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "amount", "price", "category", "is_available")
    list_display_links = ("name",)
    list_editable = ("is_available",)
    list_filter = ("is_available",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "amount", "price_at_time_purchase", "customer", "time_purchase")
    list_display_links = ("id",)
    search_fields = ("id",)


class PurchaseReturnsAdmin(admin.ModelAdmin):
    list_display = ("to_purchase", "time_request_return")
    list_display_links = ("to_purchase",)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(PurchaseReturns, PurchaseReturnsAdmin)
admin.site.register(Category, CategoryAdmin)
