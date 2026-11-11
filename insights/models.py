from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class AssignmentResult(models.Model):
    assignment = models.ForeignKey(
        "core.Assignment",
        on_delete=models.CASCADE,
        related_name="results",
    )
    cohort = models.CharField(max_length=40)
    learner_code = models.CharField(max_length=8)
    grade_percent = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(100)]
    )
    actual_minutes = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cohort", "assignment", "learner_code"],
                name="one_result_per_learner_assignment",
            ),
            models.CheckConstraint(
                condition=models.Q(grade_percent__lte=100),
                name="grade_at_most_100",
            ),
            models.CheckConstraint(
                condition=models.Q(actual_minutes__gte=1),
                name="elapsed_minutes_positive",
            ),
        ]
