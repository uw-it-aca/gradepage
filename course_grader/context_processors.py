from django.conf import settings
from userservice.user import UserService
from course_grader.dao.person import person_from_user, person_display_name


def user(request):
    try:
        user_fullname = person_display_name(person_from_user())
    except Exception as ex:
        user_fullname = None

    user_service = UserService()
    return {
        "user_login": user_service.get_user(),
        "user_fullname": user_fullname,
        "override_user": user_service.get_override_user(),
    }


def has_less_compiled(request):
    """ See if django-compressor is being used to precompile less
    """
    key = getattr(settings, "COMPRESS_PRECOMPILERS", None)
    return {"has_less_compiled": key != ()}


def debug_mode(request):
    return {"debug_mode": settings.DEBUG}
