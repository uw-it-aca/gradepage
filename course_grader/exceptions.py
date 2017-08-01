"""
Custom exceptions used by GradePage.
"""

from django.conf import settings
from django.utils.translation import ugettext as _


class InvalidUser(Exception):
    def __init__(self, identifier):
        self.identifier = identifier

    def __str__(self):
        return _("Invalid identifier '%s'" % self.identifier)


class InvalidTerm(Exception):
    def __str__(self):
        return _("receipt_not_found")


class InvalidSection(Exception):
    def __str__(self):
        return _("section_not_found")


class MissingInstructorParam(Exception):
    def __str__(self):
        return _("Missing instructor UWRegID")


class ReceiptNotFound(Exception):
    def __str__(self):
        return _("receipt_not_found")


class GradingPeriodNotOpen(Exception):
    def __str__(self):
        return _("grading_period_not_open")


class SecondaryGradingEnabled(Exception):
    def __str__(self):
        return _("secondary_grading_enabled")


class GradingNotPermitted(Exception):
    def __init__(self, section, person):
        self.section = section
        self.person = person

    def __str__(self):
        return _("grading_not_permitted")


class OverrideNotPermitted(Exception):
    def __str__(self):
        return _("no_override_submit")
