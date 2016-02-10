"""
This module encapsulates the access of sws section data
"""

from restclients.sws.section import get_section_by_url, get_section_by_label
from restclients.sws.section import get_sections_by_instructor_and_term
from restclients.sws.section import get_sections_by_delegate_and_term
from course_grader.dao.person import person_from_regid
from course_grader.exceptions import InvalidSection, MissingInstructorParam
import logging
import copy


logger = logging.getLogger(__name__)


def section_from_label(label):
    return get_section_by_label(label)


def section_from_url(url):
    return get_section_by_url(url)


def section_from_param(param):
    instructor_reg_id = None
    try:
        (year, quarter, curriculum_abbr, course_number, section_id,
            instructor_reg_id) = param.split("-", 5)
    except ValueError:
        try:
            (year, quarter, curriculum_abbr, course_number,
                section_id) = param.split("-", 4)
        except ValueError:
            raise InvalidSection("Invalid section ID: %s" % param)

    section_label = "%s,%s,%s,%s/%s" % (year, quarter, curriculum_abbr,
                                        course_number, section_id)
    section = section_from_label(section_label)

    if instructor_reg_id is None:
        raise MissingInstructorParam()

    return (section, person_from_regid(instructor_reg_id))


def all_gradable_sections(person, term):
    """
    Return a list of gradable sections for the user and term.
    """
    section_refs = get_sections_by_instructor_and_term(person, term)
    section_refs.extend(get_sections_by_delegate_and_term(person, term))

    # This sort ensures that primary sections are seen before secondaries
    section_refs.sort(key=lambda section_ref: section_ref.url)

    primary_instructors = {}
    gradable_sections = {}
    for section_ref in section_refs:
        if section_ref.url in gradable_sections:
            # Duplicate
            continue

        try:
            section = section_from_url(section_ref.url)
        except Exception as ex:
            logger.error("SKIP section for grading: %s" % ex)
            continue

        if section.current_enrollment == 0:
            # Zero enrollment
            continue

        instructors = section.get_instructors()
        if section.is_primary_section and len(instructors) == 0:
            # Primary section with zero instructors
            continue

        if section.is_independent_study:
            for instructor in instructors:
                if (instructor == person or
                        section.is_grade_submission_delegate(person)):
                    url = "%s|%s" % (section_ref.url, instructor.uwregid)
                    gradable_section = copy.deepcopy(section)
                    gradable_section.grader = instructor
                    gradable_sections[url] = gradable_section

        else:
            primary_url = section.primary_section_href
            if (not section.is_primary_section and
                    not section.allows_secondary_grading and
                    not any(r.url == primary_url for r in section_refs)):
                # Secondary grading is not enabled and this user doesn't
                # have the primary section in their list
                continue

            if section.is_primary_section:
                primary_instructors[section_ref.url] = instructors
            else:
                if primary_url not in primary_instructors:
                    try:
                        primary_instructors[primary_url] = get_section_by_url(
                            primary_url).get_instructors()
                    except Exception as ex:
                        logger.error("SKIP section for grading: %s" % ex)
                        continue

            if (section.is_instructor(person) or (
                    not section.is_primary_section and
                    person in primary_instructors.get(primary_url, []))):
                # User is instructor or instructor of primary section
                instructor = person

            elif section.is_grade_submission_delegate(person):
                # For a delegate, find the primary instructor for:
                #   Primary sections
                #   Secondary sections lacking explicit instructors
                #   Secondary sections without secondary grading enabled
                if section.is_primary_section:
                    try:
                        instructor = instructors[0]
                    except IndexError:
                        continue

                else:  # Secondary
                    if (not section.allows_secondary_grading or
                            len(instructors) == 0):
                        try:
                            instructor = primary_instructors.get(primary_url,
                                                                 [])[0]
                        except IndexError:
                            continue
                    else:
                        instructor = instructors[0]

            else:
                # No grading role for user
                continue

            if instructor is not None:
                section.grader = instructor
                gradable_sections[section_ref.url] = section

    return gradable_sections.values()


def is_grader_for_section(section, person):
    if (section.is_instructor(person) or
            section.is_grade_submission_delegate(person)):
        return True

    elif not section.is_primary_section:
        primary_url = section.primary_section_href
        primary_section = get_section_by_url(primary_url)
        return is_grader_for_section(primary_section, person)

    else:
        return False
