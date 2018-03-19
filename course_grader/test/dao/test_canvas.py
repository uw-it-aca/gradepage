from django.test import TestCase
from course_grader.dao.canvas import *
from uw_canvas.models import Assignment


class CanvasDAOFunctionsTest(TestCase):
    def test_muted_assignment(self):
        assignment = Assignment(
            muted=False, published=False, has_submissions=False)
        self.assertEquals(assignment_muted(assignment), False)

        assignment = Assignment(
            muted=True, published=False, has_submissions=False)
        self.assertEquals(assignment_muted(assignment), False)

        assignment = Assignment(
            muted=True, published=True, has_submissions=True)
        self.assertEquals(assignment_muted(assignment), True)

        assignment = Assignment(
            muted=True, published=True, has_submissions=False)
        self.assertEquals(assignment_muted(assignment), True)

        assignment = Assignment(
            muted=True, published=False, has_submissions=True)
        self.assertEquals(assignment_muted(assignment), True)
