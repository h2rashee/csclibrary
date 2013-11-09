import grp
import os

import exceptions

class _PermissionLevel:
    def __init__(self, group_name, pretty_name):
        self.group_name = group_name
        self.pretty_name = pretty_name

PERMISSION_OFFICE = _PermissionLevel("office", "Office worker")
PERMISSION_LIBCOM = _PermissionLevel("libcom", "Library Committee")

def check_permissions(permission_level):
    def decorator(fn):
        def wrapped_function(*args, **kwargs):
            if not has_permission(permission_level):
                raise exceptions.PermissionsError(permission_level.pretty_name)
            return fn(*args, **kwargs)

        return wrapped_function

    return decorator

def has_permission(permission_level):
    return permission_level.group_name in _CURRENT_GROUPS_GETTER()

def _current_group_names():
    group_ids = os.getgroups()
    group_names = [grp.getgrgid(group_id).gr_name for group_id in group_ids]
    return group_names

# Hack to allow dependency injection for testing
_CURRENT_GROUPS_GETTER = _current_group_names
