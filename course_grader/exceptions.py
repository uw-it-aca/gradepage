# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


"""
Custom exceptions used by GradePage.
"""

from django.conf import settings


class InvalidUser(Exception):
    def __init__(self, identifier):
        self.identifier = identifier

    def __str__(self):
        return "Invalid identifier '{}'".format(self.identifier)


class InvalidTerm(Exception):
    def __str__(self):
        return "No submission information available"


class InvalidSection(Exception):
    def __str__(self):
        return "Section not found."


class InvalidGradingScale(Exception):
    def __str__(self):
        return "Invalid Grading Scale"


class MissingInstructorParam(Exception):
    def __str__(self):
        return "Missing instructor UWRegID"


class ReceiptNotFound(Exception):
    def __str__(self):
        return "No submission information available"


class GradingPeriodNotOpen(Exception):
    def __str__(self):
        return "Grade submission is not open for this section."


class SecondaryGradingEnabled(Exception):
    def __str__(self):
        return ("Secondary grading is enabled for this course. Final grades "
                "must be submitted separately for each secondary section.")


class GradingNotPermitted(Exception):
    def __init__(self, section, person):
        self.section = section
        self.person = person

    def __str__(self):
        return "You are not authorized to submit grades for this section."


class OverrideNotPermitted(Exception):
    def __str__(self):
        return "Cannot submit grades while using admin override."


class GradesNotSubmitted(Exception):
    def __str__(self):
        return "No grades were submitted"


class InvalidCSV(Exception):
    def __init__(self, error="Invalid CSV file"):
        self.error = error

    def __str__(self):
        return self.error
