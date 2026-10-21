from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Workspace(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="workspaces"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Board(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="boards"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Column(models.Model):
    name = models.CharField(max_length=100)
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="columns"
    )
    position = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.board.name} - {self.name}"


class Task(models.Model):

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    column = models.ForeignKey(
        Column,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title