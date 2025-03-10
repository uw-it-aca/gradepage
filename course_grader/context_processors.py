# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from course_grader.dao.term import current_term
from course_grader.dao.message import get_messages_for_term
from restclients_core.exceptions import DataFailureException


def persistent_messages(request):
    try:
        return get_messages_for_term(current_term())
    except DataFailureException:
        pass
