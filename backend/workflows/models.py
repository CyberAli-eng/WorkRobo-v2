"""User-scoped workflow domain models.

Workflow, Node, Edge, WorkflowRun all inherit ``UserScopedModel`` and so
get the ``user`` FK and ``UserScopedManager``. Every read/write in views
MUST go through ``Model.objects.for_user(request.user)`` — the manager
filters at the root, so attempting to fetch another user's row by
guessing IDs raises ``DoesNotExist``.
"""
from django.db import models

from core.models import UserScopedModel


class Workflow(UserScopedModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self) -> str:
        return self.name


class Node(UserScopedModel):
    KIND_CHOICES = [
        ("trigger", "Trigger"),
        ("action", "Action"),
        ("condition", "Condition"),
        ("output", "Output"),
    ]

    workflow = models.ForeignKey(
        Workflow, on_delete=models.CASCADE, related_name="nodes"
    )
    kind = models.CharField(max_length=32, choices=KIND_CHOICES, default="action")
    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.workflow_id}:{self.kind}#{self.pk}"


class Edge(UserScopedModel):
    workflow = models.ForeignKey(
        Workflow, on_delete=models.CASCADE, related_name="edges"
    )
    source = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name="outgoing_edges"
    )
    target = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name="incoming_edges"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("id",)
        # An edge's endpoints belong to the same workflow.
        constraints = [
            models.UniqueConstraint(
                fields=("workflow", "source", "target"),
                name="unique_edge_per_workflow",
            )
        ]

    def __str__(self) -> str:
        return f"{self.source_id}->{self.target_id}"


class WorkflowRun(UserScopedModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    workflow = models.ForeignKey(
        Workflow, on_delete=models.CASCADE, related_name="runs"
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Run#{self.pk} ({self.workflow_id}, {self.status})"
