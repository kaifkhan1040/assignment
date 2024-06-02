# from ..base.api.permissions import (IsAuthenticated, PermissionComponent, ResourcePermission,
#                                           IsGetMethodOrAuthenticated, AllowAny)


# class IsTheSameUser(PermissionComponent):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated()

#     def has_object_permission(self, request, view, obj=None):
#         return request.user.is_authenticated() and request.user.pk == obj.pk
    
# class UserPermissions(ResourcePermission):
#     metadata_perms = IsAuthenticated()
#     enough_perms = IsAuthenticated()
#     global_perms = None
#     retrieve_perms = IsAuthenticated()
#     create_perms = IsAuthenticated()
#     update_perms = IsAuthenticated()
#     partial_update_perms = IsAuthenticated()
#     destroy_perms = IsAuthenticated()
#     list_perms = IsGetMethodOrAuthenticated()