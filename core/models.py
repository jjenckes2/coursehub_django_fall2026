from django.db import models

class Assignment(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    completed = models.BooleanField(default=False)
    estimated_minutes = models.PositiveIntegerField(default=30)

    def __str_(self):
        return self.title
