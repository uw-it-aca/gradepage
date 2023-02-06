# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.test import TestCase
from course_grader.exceptions import *


class ExceptionsTest(TestCase):
    def test_InvalidUser(self):
        try:
            raise InvalidUser('javerage')
        except InvalidUser as ex:
            self.assertEquals(str(ex), "Invalid identifier 'javerage'")

    def test_InvalidTerm(self):
        try:
            raise InvalidTerm()
        except InvalidTerm as ex:
            self.assertEquals(str(ex), "No submission information available")

    def test_InvalidSection(self):
        try:
            raise InvalidSection()
        except InvalidSection as ex:
            self.assertEquals(str(ex), "Section not found.")

    def test_MissingInstructorParam(self):
        try:
            raise MissingInstructorParam()
        except MissingInstructorParam as ex:
            self.assertEquals(str(ex), "Missing instructor UWRegID")

    def test_ReceiptNotFound(self):
        try:
            raise ReceiptNotFound()
        except ReceiptNotFound as ex:
            self.assertEquals(str(ex), "No submission information available")

    def test_GradingPeriodNotOpen(self):
        try:
            raise GradingPeriodNotOpen()
        except GradingPeriodNotOpen as ex:
            self.assertEquals(str(ex), ("Grade submission is not open for "
                                        "this section."))

    def test_SecondaryGradingEnabled(self):
        try:
            raise SecondaryGradingEnabled()
        except SecondaryGradingEnabled as ex:
            self.assertEquals(str(ex), (
               "Secondary grading is enabled for this course. Final grades "
               "must be submitted separately for each secondary section."))

    def test_GradingNotPermitted(self):
        section = None
        person = None
        try:
            raise GradingNotPermitted(section, person)
        except GradingNotPermitted as ex:
            self.assertEquals(
                str(ex),
                "You are not authorized to submit grades for this section.")

    def test_OverrideNotPermitted(self):
        try:
            raise OverrideNotPermitted()
        except OverrideNotPermitted as ex:
            self.assertEquals(
                str(ex), "Cannot submit grades while using admin override.")

    def test_GradesNotSubmitted(self):
        try:
            raise GradesNotSubmitted()
        except GradesNotSubmitted as ex:
            self.assertEquals(str(ex), "No grades were submitted")

    def test_InvalidCSV(self):
        try:
            raise InvalidCSV("Missing header")
        except InvalidCSV as ex:
            self.assertEquals(str(ex), "Missing header")

        try:
            raise InvalidCSV()
        except InvalidCSV as ex:
            self.assertEquals(str(ex), "Invalid CSV file")
