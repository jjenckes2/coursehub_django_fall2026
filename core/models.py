from django.conf import settings  # added for Oct 26 lecture: use the configured user model.
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name



class Assignment(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    completed = models.BooleanField(default=False)
    estimated_minutes = models.PositiveIntegerField(default=30)
    #add here Oct 26 lecture
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments",
    )
    #for Oct 26 lecture: display assignment titles in the admin.
    def __str__(self):
        return self.title
