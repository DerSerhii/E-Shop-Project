"""This is the urls of application E_SHOP"""


from django.urls import path

from .views import ShopHome, ProductCategory, ShowProduct, RegisterCustomer, \
    Login, Logout, BuyView, WalletCustomer, AdminAddProduct, \
    AdminAddCategory, AdminEditProduct, AdminEditCategory, ShowPurchase, \
    RefundPurchase, AdminShowRefundPurchase, AdminRemoveRefundPurchase, AdminApproveRefundPurchase

urlpatterns = [
    path('', ShopHome.as_view(), name='home'),

    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('register/', RegisterCustomer.as_view(), name='register'),
    path('add-product/', AdminAddProduct.as_view(), name='add-product'),
    path('add-category/', AdminAddCategory.as_view(), name='add-category'),
    path('edit-product/<slug:prod_slug>', AdminEditProduct.as_view(), name='edit-product'),
    path('edit-category/<slug:cat_slug>', AdminEditCategory.as_view(), name='edit-category'),
    path('category/<slug:cat_slug>/', ProductCategory.as_view(), name='category'),
    path('product/<slug:prod_slug>/', ShowProduct.as_view(), name='product'),
    path('product/buy/<slug:prod_slug>/', BuyView.as_view(), name='product-buy'),
    path('customer/wallet/<int:cust_id>/', WalletCustomer.as_view(), name='wallet'),
    path('customer/purchase/', ShowPurchase.as_view(), name='purchase'),
    path('refund-purchase/<int:pur_id>/', RefundPurchase.as_view(), name='refund-purchase'),
    path('admin-refund/', AdminShowRefundPurchase.as_view(), name='admin-refund'),
    path('admin-refund-remove/<int:ref_id>/', AdminRemoveRefundPurchase.as_view(), name='admin-refund-remove'),
    path('admin-refund-approve/<int:ref_id>/', AdminApproveRefundPurchase.as_view(), name='admin-refund-approve'),
]
