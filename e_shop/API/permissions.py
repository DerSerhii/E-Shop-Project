from rest_framework import permissions
from rest_framework.permissions import IsAdminUser, SAFE_METHODS


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user and
            request.user.is_staff)


class CustomerBuyAndReadOrAdminReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(
                request.user and
                request.user.is_authenticated)
        if request.method == "POST":
            return bool(
                request.user and
                request.user.is_authenticated and
                not request.user.is_staff)
        return False


class CustomerRefundAndReadOrAdminRefundAndRead(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(
                request.user and
                request.user.is_authenticated)
        if request.method == "POST":
            return bool(
                request.user and
                request.user.is_authenticated and
                not request.user.is_staff)
        if request.method == "DELETE":
            return bool(
                request.user and
                request.user.is_staff)
        return False
