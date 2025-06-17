from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            hasattr(request.user, "role")
            and request.user.role.name == "admin"
            and request.user.status == 1
        )


class IsSale(BasePermission):
    def has_permission(self, request, view):
        return (
            hasattr(request.user, "role")
            and request.user.role.name == "sale"
            and request.user.status == 1
        )


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return (
            hasattr(request.user, "role")
            and request.user.role.name == "customer"
            and request.user.status == 1
        )


class IsAdminOrSale(BasePermission):
    def has_permission(self, request, view):
        return (
            hasattr(request.user, "role")
            and request.user.role.name in ["admin", "sale"]
            and request.user.status == 1
        )
