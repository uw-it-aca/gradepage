"""
This module encapsulates the interactions with catalyst gradebook
"""

from uw_catalyst.gradebook import (
    get_participants_for_section, get_participants_for_gradebook,
    valid_gradebook_id)


def grades_for_section(section, instructor, gradebook_id=None):
    if gradebook_id is not None:
        participants = get_participants_for_gradebook(gradebook_id, instructor)
    else:
        participants = get_participants_for_section(section, instructor)

    grade_data = {"grades": []}
    for participant in participants:
        grade_data["grades"].append(participant.json_data())

    return grade_data
