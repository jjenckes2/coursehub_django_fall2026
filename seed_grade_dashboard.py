from core.models import Assignment
from insights.models import AssignmentResult

assignments = list(Assignment.objects.order_by("pk")[:4])
if len(assignments) < 4:
    raise ValueError("Add at least four assignments in CourseHub, then run again.")

grade_sets = [
    [80, 88, 96],
    [72, 80, 88],
    [84, 90, 96],
    [68, 74, 80],
]

minute_sets = [
    [25, 40, 55],
    [45, 30, 65],
    [35, 50, 42],
    [60, 75, 48],
]

for assignment, grades, minutes in zip(assignments, grade_sets, minute_sets):
    for number, (grade, elapsed) in enumerate(zip(grades, minutes), start=1):
        AssignmentResult.objects.update_or_create(
            cohort="fall_2026",
            assignment=assignment,
            learner_code=f"S{number:02}",
            defaults={"grade_percent": grade, "actual_minutes": elapsed},
        )
    print(assignment.pk, assignment.title)

print("Created or updated 12 synthetic results.")
