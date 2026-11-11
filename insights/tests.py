import base64
from collections import defaultdict
from contextlib import redirect_stdout
from datetime import date
from io import StringIO
import json
from pathlib import Path
import runpy

import numpy as np
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from core.models import Assignment
from .models import AssignmentResult


class DashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = get_user_model().objects.create_user(
            username="instructor", is_staff=True,
        )
        cls.learner = get_user_model().objects.create_user(username="learner")
        cls.assignments = [
            Assignment.objects.create(title=title, due_date=date(2026, 11, 11))
            for title in ("HTML", "CSS", "Django", "JavaScript")
        ]
        cls.url = reverse("insights:dashboard")

    def seed_results(self):
        script = Path(__file__).resolve().parent.parent / "seed_grade_dashboard.py"
        with redirect_stdout(StringIO()):
            runpy.run_path(str(script))

    def chart(self, response, name):
        # Inspect the actual figure data sent to Plotly.js in the rendered page.
        arguments = response.context[name].split("Plotly.newPlot(", 1)[1].lstrip()
        decoder = json.JSONDecoder()
        _, end = decoder.raw_decode(arguments)
        arguments = arguments[end:].lstrip()[1:].lstrip()
        traces, end = decoder.raw_decode(arguments)
        layout, _ = decoder.raw_decode(arguments[end:].lstrip()[1:].lstrip())
        return traces[0], layout

    def values(self, trace, axis):
        values = trace[axis]
        if isinstance(values, dict):
            return np.frombuffer(
                base64.b64decode(values["bdata"]), dtype=values["dtype"],
            ).tolist()
        return values

    def test_dashboard_requires_staff(self):
        login_url = f"{reverse('login')}?next={self.url}"
        self.assertRedirects(self.client.get(self.url), login_url)
        self.client.force_login(self.learner)
        self.assertRedirects(self.client.get(self.url), login_url)

    def test_inactive_staff_cannot_access_dashboard(self):
        self.staff.is_active = False
        self.staff.save()
        self.client.force_login(self.staff)
        self.assertRedirects(
            self.client.get(self.url), f"{reverse('login')}?next={self.url}",
        )

    def test_nav_link_is_visible_to_staff_and_api_client_link_is_removed(self):
        for user, show_dashboard in ((None, False), (self.learner, False), (self.staff, True)):
            with self.subTest(user=user):
                if user:
                    self.client.force_login(user)
                response = self.client.get(reverse("core:home"))
                self.assertNotContains(response, reverse("api-client"))
                if show_dashboard:
                    self.assertContains(response, f'href="{self.url}"')
                else:
                    self.assertNotContains(response, f'href="{self.url}"')

    def test_empty_dashboard_has_a_useful_message(self):
        self.client.force_login(self.staff)
        response = self.client.get(self.url)
        self.assertContains(response, "No demo results yet")
        self.assertNotContains(response, "Plotly.newPlot")
        self.assertNotContains(response, "cdn.plot.ly")

    def test_seeded_dashboard_embeds_three_plots_and_the_individual_results(self):
        self.seed_results()
        self.client.force_login(self.staff)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        average, _ = self.chart(response, "average_chart")
        self.assertEqual(average["histfunc"], "avg")
        grades_by_assignment = defaultdict(list)
        for label, grade in zip(self.values(average, "x"), self.values(average, "y")):
            grades_by_assignment[label].append(grade)
        self.assertEqual(
            [sum(grades) / len(grades) for grades in grades_by_assignment.values()],
            [88, 80, 90, 74],
        )
        histogram, _ = self.chart(response, "histogram_chart")
        self.assertEqual(histogram["type"], "histogram")
        self.assertEqual(
            self.values(histogram, "x"),
            [80, 88, 96, 72, 80, 88, 84, 90, 96, 68, 74, 80],
        )
        scatter, _ = self.chart(response, "scatter_chart")
        self.assertEqual(scatter["mode"], "markers")
        points = list(zip(self.values(scatter, "x"), self.values(scatter, "y")))
        self.assertEqual(len(points), 12)
        for pair in ((25, 80), (55, 96), (75, 74)):
            self.assertIn(pair, points)
        self.assertContains(response, "Plotly.newPlot", count=3)
        self.assertContains(response, 'src="https://cdn.plot.ly/', count=1)
        self.assertNotContains(response, "CanvasJS")
        self.assertContains(response, '<th scope="row">', count=12)
        self.assertEqual(len(response.context["results"]), 12)
        self.assertContains(response, 'aria-current="page">Grade Dashboard')

    def test_histogram_passes_boundary_grades_to_plotly_without_clipping(self):
        for number, grade in enumerate((0, 9, 10, 89, 90, 100)):
            AssignmentResult.objects.create(
                assignment=self.assignments[0], cohort="fall_2026",
                learner_code=f"S{number}", grade_percent=grade,
                actual_minutes=number + 1,
            )
        self.client.force_login(self.staff)
        response = self.client.get(self.url)
        histogram, layout = self.chart(response, "histogram_chart")
        self.assertEqual(self.values(histogram, "x"), [0, 9, 10, 89, 90, 100])
        self.assertNotIn("xbins", histogram)
        self.assertNotIn("range", layout["xaxis"])

    def test_identical_titles_remain_separate_and_other_cohorts_are_excluded(self):
        for assignment, grade in zip(self.assignments[:2], (20, 80)):
            assignment.title = "Same title"
            assignment.save()
            AssignmentResult.objects.create(
                assignment=assignment, cohort="fall_2026",
                learner_code="S01", grade_percent=grade, actual_minutes=30,
            )
        AssignmentResult.objects.create(
            assignment=self.assignments[0], cohort="another-cohort",
            learner_code="S01", grade_percent=100, actual_minutes=200,
        )
        self.client.force_login(self.staff)
        response = self.client.get(self.url)
        average, _ = self.chart(response, "average_chart")
        self.assertEqual(self.values(average, "x"), [
            f"Same title (#{assignment.pk})" for assignment in self.assignments[:2]
        ])
        self.assertEqual(self.values(average, "y"), [20, 80])
        self.assertEqual(len(response.context["results"]), 2)

    def test_assignment_titles_are_safely_encoded_for_javascript(self):
        assignment = self.assignments[0]
        assignment.title = '</script><script>alert("test")</script>'
        assignment.save()
        self.seed_results()
        self.client.force_login(self.staff)
        response = self.client.get(self.url)
        self.assertNotContains(response, assignment.title)
        self.assertContains(response, "&lt;/script&gt;")
        for name in ("average_chart", "histogram_chart", "scatter_chart"):
            self.assertNotIn(assignment.title, response.context[name])
        average, _ = self.chart(response, "average_chart")
        self.assertIn(assignment.title, self.values(average, "x")[0])

    def test_changing_a_score_updates_every_plot_on_refresh(self):
        self.seed_results()
        result = AssignmentResult.objects.order_by("assignment_id", "learner_code").first()
        result.grade_percent = 95
        result.save()
        self.client.force_login(self.staff)
        response = self.client.get(self.url)
        average, _ = self.chart(response, "average_chart")
        self.assertEqual(sum(self.values(average, "y")[:3]) / 3, 93)
        histogram, _ = self.chart(response, "histogram_chart")
        self.assertEqual(self.values(histogram, "x")[0], 95)
        scatter, _ = self.chart(response, "scatter_chart")
        self.assertEqual((self.values(scatter, "x")[0], self.values(scatter, "y")[0]), (25, 95))
        self.assertEqual(response.context["results"][0]["grade_percent"], 95)

    def test_seed_script_is_repeatable_and_preserves_assignments(self):
        original = list(Assignment.objects.order_by("pk").values())
        self.seed_results()
        result = AssignmentResult.objects.order_by("pk").first()
        result.grade_percent = 1
        result.save()
        self.seed_results()
        result.refresh_from_db()
        self.assertEqual(result.grade_percent, 80)
        self.assertEqual(AssignmentResult.objects.count(), 12)
        self.assertEqual(list(Assignment.objects.order_by("pk").values()), original)

    def test_seed_script_requires_four_assignments_before_creating_results(self):
        self.assignments[-1].delete()
        with self.assertRaisesMessage(ValueError, "Add at least four assignments"):
            self.seed_results()
        self.assertEqual(AssignmentResult.objects.count(), 0)


class AssignmentResultTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.assignment = Assignment.objects.create(
            title="Web development", due_date=date(2026, 11, 11),
        )

    def create_result(self, **changes):
        data = {
            "assignment": self.assignment, "cohort": "nov11-canvasjs",
            "learner_code": "S01", "grade_percent": 80, "actual_minutes": 30,
        }
        data.update(changes)
        return AssignmentResult.objects.create(**data)

    def test_database_rejects_grades_outside_range_and_zero_minutes(self):
        for changes in ({"grade_percent": -1}, {"grade_percent": 101}, {"actual_minutes": 0}):
            with self.subTest(changes=changes):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    self.create_result(**changes)

    def test_learner_result_is_unique_within_assignment_and_cohort(self):
        self.create_result()
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.create_result()
        self.create_result(cohort="another-cohort")
        self.assertEqual(self.assignment.results.count(), 2)

    def test_assignment_deletion_removes_related_results(self):
        self.create_result()
        self.assignment.delete()
        self.assertFalse(AssignmentResult.objects.exists())
