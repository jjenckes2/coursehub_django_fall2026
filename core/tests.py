from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import AssignmentForm, AssignmentUpdateForm
from .models import Assignment, Category


class CategoryRelationshipTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_user(username="owner")
        cls.category = Category.objects.create(name="Web")
        cls.assignment = Assignment.objects.create(
            title="Build a template",
            due_date=date(2026, 11, 2),
            owner=cls.owner,
            category=cls.category,
        )

    def test_relationship_can_be_queried_in_both_directions(self):
        empty_category = Category.objects.create(name="Database")

        self.assertEqual(self.assignment.category, self.category)
        self.assertQuerySetEqual(
            self.category.assignments.all(), [self.assignment]
        )
        self.assertQuerySetEqual(
            Assignment.objects.filter(category__name="Web"), [self.assignment]
        )
        self.assertFalse(empty_category.assignments.exists())

    def test_deleting_category_preserves_assignment_and_owner(self):
        original = Assignment.objects.values().get(pk=self.assignment.pk)

        self.category.delete()

        original["category_id"] = None
        self.assertEqual(
            Assignment.objects.values().get(pk=self.assignment.pk), original
        )

    def test_deleting_assignment_preserves_category(self):
        self.assignment.delete()

        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())
        self.assertFalse(self.category.assignments.exists())


class PublicCategoryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_user(username="owner")
        cls.other_user = get_user_model().objects.create_user(username="other")
        cls.category = Category.objects.create(name="Web")
        cls.assignment = Assignment.objects.create(
            title="Build a template",
            due_date=date(2026, 11, 2),
            owner=cls.owner,
            category=cls.category,
        )

    def assignment_data(self, **changes):
        data = {
            "title": "Add a list filter",
            "description": "",
            "due_date": "2026-11-04",
            "estimated_minutes": "45",
            "category": str(self.category.pk),
        }
        data.update(changes)
        return data

    def test_create_with_category_uses_logged_in_owner(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("core:assignment_create"),
            self.assignment_data(owner=str(self.other_user.pk)),
        )

        assignment = Assignment.objects.get(title="Add a list filter")
        self.assertRedirects(
            response, reverse("core:assignment_detail", args=[assignment.pk])
        )
        self.assertEqual(assignment.category, self.category)
        self.assertEqual(assignment.owner, self.owner)
        self.assertFalse(assignment.completed)

    def test_create_without_category_is_valid(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("core:assignment_create"), self.assignment_data(category="")
        )

        self.assertEqual(response.status_code, 302)
        self.assertIsNone(
            Assignment.objects.get(title="Add a list filter").category_id
        )

    def test_owner_can_change_and_clear_category(self):
        self.client.force_login(self.owner)
        category = Category.objects.create(name="Database")
        url = reverse("core:assignment_update", args=[self.assignment.pk])

        for selected, expected in ((str(category.pk), category.pk), ("", None)):
            with self.subTest(category=selected):
                response = self.client.post(
                    url,
                    self.assignment_data(
                        category=selected,
                        completed="on",
                        owner=str(self.other_user.pk),
                    ),
                )

                self.assertEqual(response.status_code, 302)
                self.assignment.refresh_from_db()
                self.assertEqual(self.assignment.category_id, expected)
                self.assertEqual(self.assignment.owner, self.owner)
                self.assertTrue(self.assignment.completed)

    def test_shared_category_does_not_grant_edit_or_delete_permission(self):
        Assignment.objects.create(
            title="Other user's work",
            due_date=date(2026, 11, 4),
            owner=self.other_user,
            category=self.category,
        )
        self.client.force_login(self.other_user)

        for action in ("assignment_update", "assignment_delete"):
            url = reverse(f"core:{action}", args=[self.assignment.pk])
            for method in (self.client.get, self.client.post):
                with self.subTest(action=action, method=method.__name__):
                    response = method(url, self.assignment_data(category=""))
                    self.assertEqual(response.status_code, 404)

        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.category, self.category)
        self.assertEqual(self.assignment.owner, self.owner)

    def test_detail_displays_selected_category_or_empty_label(self):
        url = reverse("core:assignment_detail", args=[self.assignment.pk])

        response = self.client.get(url)
        self.assertContains(response, "<dt>Category</dt><dd>Web</dd>", html=True)

        self.assignment.category = None
        self.assignment.save()
        response = self.client.get(url)
        self.assertContains(
            response, "<dt>Category</dt><dd>Not assigned</dd>", html=True
        )

    def test_category_keeps_existing_duration_validation(self):
        for form_class in (AssignmentForm, AssignmentUpdateForm):
            for minutes in (0, 481):
                with self.subTest(form=form_class.__name__, minutes=minutes):
                    form = form_class(
                        data=self.assignment_data(estimated_minutes=str(minutes))
                    )
                    self.assertFalse(form.is_valid())
                    self.assertIn("estimated_minutes", form.errors)


class CategoryAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.administrator = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="test-password"
        )
        cls.owner = get_user_model().objects.create_user(username="owner")
        cls.category = Category.objects.create(name="Web")
        cls.assignment = Assignment.objects.create(
            title="Build a template",
            due_date=date(2026, 11, 2),
            owner=cls.owner,
            category=cls.category,
        )

    def setUp(self):
        self.client.force_login(self.administrator)

    def test_assignment_list_searches_and_filters_by_category(self):
        other_category = Category.objects.create(name="Database")
        Assignment.objects.create(
            title="Design tables",
            due_date=date(2026, 11, 4),
            category=other_category,
        )
        url = reverse("admin:core_assignment_changelist")

        for query in ({"q": "Web"}, {"category__id__exact": self.category.pk}):
            with self.subTest(query=query):
                response = self.client.get(url, query)
                self.assertEqual(response.status_code, 200)
                self.assertQuerySetEqual(
                    response.context["cl"].result_list, [self.assignment]
                )

    def test_assignment_list_can_save_completion(self):
        response = self.client.post(
            reverse("admin:core_assignment_changelist"),
            {
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "1",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-id": str(self.assignment.pk),
                "form-0-completed": "on",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assignment.refresh_from_db()
        self.assertTrue(self.assignment.completed)

    def test_category_inline_updates_and_adds_assignments(self):
        url = reverse("admin:core_category_change", args=[self.category.pk])
        response = self.client.get(url)
        self.assertContains(
            response,
            reverse("admin:core_assignment_change", args=[self.assignment.pk]),
        )

        response = self.client.post(
            url,
            {
                "name": "Web",
                "assignments-TOTAL_FORMS": "2",
                "assignments-INITIAL_FORMS": "1",
                "assignments-MIN_NUM_FORMS": "0",
                "assignments-MAX_NUM_FORMS": "1000",
                "assignments-0-id": str(self.assignment.pk),
                "assignments-0-category": str(self.category.pk),
                "assignments-0-title": self.assignment.title,
                "assignments-0-owner": str(self.owner.pk),
                "assignments-0-due_date": "2026-11-02",
                "assignments-0-completed": "on",
                "assignments-1-category": str(self.category.pk),
                "assignments-1-title": "Add a list filter",
                "assignments-1-owner": str(self.owner.pk),
                "assignments-1-due_date": "2026-11-04",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assignment.refresh_from_db()
        self.assertTrue(self.assignment.completed)
        self.assertEqual(self.assignment.owner, self.owner)
        added = self.category.assignments.get(title="Add a list filter")
        self.assertEqual(added.owner, self.owner)
        self.assertEqual(added.estimated_minutes, 30)
        self.assertEqual(added.description, "")
