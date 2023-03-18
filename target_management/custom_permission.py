from rest_framework import permissions


class UserObjectAcessPermission(permissions.BasePermission):

    message = "not allowed to view other user's objects"

    def has_object_permission(self, request, view, obj):
        print('i am called')

    # def has_permission(self, request, view):
    #     print('has permission called')