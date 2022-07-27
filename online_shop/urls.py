"""online_shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from online_shop import settings
from e_shop.API.resources import RegisterView, LogoutView, LogoutAllView, \
    ProductViewSet, PurchaseViewSet, CategoryViewSet, RefundPurchaseViewSet

router = routers.SimpleRouter()
router.register('shop-home', ProductViewSet)
router.register('category', CategoryViewSet)
router.register('purchase', PurchaseViewSet)
router.register('refund', RefundPurchaseViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('e_shop.urls')),
    path('api/', include(router.urls)),
    path('api-token-auth/', obtain_auth_token),
    path('api/login/token-jwd/', TokenObtainPairView.as_view()),
    path('api/login/token-jwd/refresh/', TokenRefreshView.as_view()),
    path('api/logout/', LogoutView.as_view()),
    path('api/logout-all/', LogoutAllView.as_view()),
    path('api/register/', RegisterView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
