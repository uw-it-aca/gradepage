# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from course_grader.dao.term import current_term
from course_grader.dao.message import get_messages_for_term
from course_grader.exceptions import DataFailureException
from logging import getLogger

logger = getLogger(__name__)


def persistent_messages(request):
    try:
        return get_messages_for_term(current_term())
    except DataFailureException as ex:
        logger.error(f"Persistent messages failed to load! {ex}")
        return {"messages": []}
