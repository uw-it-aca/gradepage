"""
This module encapsulates the interactions with the restclients.pws,
provides identity information
"""

from restclients.pws import PWS
from restclients.exceptions import InvalidNetID, DataFailureException
from userservice.user import UserService
from course_grader.exceptions import InvalidUser
import json


def person_from_username(username):
    try:
        return PWS().get_person_by_netid(username.lower())
    except InvalidNetID as ex:
        raise InvalidUser()
    except DataFailureException as ex:
        if ex.status == 404:
            raise InvalidUser()
        else:
            raise


def person_from_user():
    return person_from_username(UserService().get_user())


def person_from_regid(regid):
    return PWS().get_person_by_regid(regid)


def is_netid(username):
    error_msg = "No override user supplied, please enter a UWNetID"
    if len(username) > 0:
        try:
            person = PWS().get_person_by_netid(username)
            if username.lower() == person.uwnetid:
                error_msg = None
            else:
                error_msg = "Current netid: %s, Prior netid: " % person.uwnetid
        except InvalidNetID:
            error_msg = "Not a valid UWNetID: "
        except DataFailureException, err:
            data = json.loads(err.msg)
            error_msg = "%s: " % data["StatusDescription"].rstrip(".")
    return error_msg
