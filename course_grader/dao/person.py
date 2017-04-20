"""
This module encapsulates the interactions with the restclients.pws,
provides identity information
"""

from uw_pws import PWS
from restclients_core.exceptions import (
    InvalidNetID, InvalidRegID, DataFailureException)
from course_grader.exceptions import InvalidUser
from userservice.user import UserService
from nameparser import HumanName
import json


def person_from_netid(netid):
    try:
        return PWS().get_person_by_netid(netid)
    except (InvalidNetID, AttributeError) as ex:
        raise InvalidUser(ex)
    except DataFailureException as ex:
        if ex.status == 404:
            raise InvalidUser(ex)
        else:
            raise


def person_from_user():
    return person_from_netid(UserService().get_user())


def person_from_request(request):
    return person_from_netid(request.META.get('HTTP_X_UW_ACT_AS'))


def person_from_regid(regid):
    try:
        return PWS().get_person_by_regid(regid)
    except InvalidRegID as ex:
        raise InvalidUser(ex)
    except DataFailureException as ex:
        if ex.status == 404:
            raise InvalidUser(ex)
        else:
            raise


def person_display_name(person):
    if (person.display_name is not None and len(person.display_name) and
            not person.display_name.isupper()):
        name = person.display_name
    else:
        name = HumanName("%s %s" % (person.first_name, person.surname))
        name.capitalize()
        name.string_format = "{first} {last}"
    return str(name)


def is_netid(username):
    error_msg = "No override user supplied, please enter a UWNetID"
    if username is not None and len(username) > 0:
        try:
            person = person_from_netid(username)
            if username.lower() == person.uwnetid:
                error_msg = None
            else:
                error_msg = "Current netid: %s, Prior netid: " % person.uwnetid
        except InvalidUser:
            error_msg = "Not a valid UWNetID: "
        except DataFailureException as err:
            data = json.loads(err.msg)
            error_msg = "%s: " % data["StatusDescription"].rstrip(".")
    return error_msg
