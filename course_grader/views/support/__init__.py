from django.conf import settings
from userservice.user import UserService
from authz_group import Group


def is_admin_user():
    return Group().is_member_of_group(UserService().get_original_user(),
                                      settings.GRADEPAGE_ADMIN_GROUP)
