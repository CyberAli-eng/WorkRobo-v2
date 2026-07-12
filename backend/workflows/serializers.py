"""DRF serializers for the workflow domain.

Validation: when creating a Node/Edge/WorkflowRun, the related Workflow
must belong to the request user. We check this against the request
user's queryset (``Workflow.objects.for_user(...)``) so an attacker
cannot reference another user's workflow by ID.
"""
from rest_framework import serializers

from .models import Edge, Node, Workflow, WorkflowRun


class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = ("id", "name", "description", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = (
            "id", "workflow", "kind", "position_x", "position_y",
            "config", "created_at",
        )
        read_only_fields = ("id", "created_at")
    def validate_workflow(self, workflow: Workflow) -> Workflow:
        request = self.context.get("request")
        if request is None or workflow.user_id != request.user.id:
            # The workflow is not in the caller's scope. Treat as 404
            # to avoid leaking existence.
            raise serializers.ValidationError("Invalid workflow.")
        return workflow
    
    _FORBIDDEN_CONFIG_KEYS = {"api_key", "apikey", "token", "secret", "password", "credential", "credential_value"}
    def validate_config(self, value):
        if not isinstance(value, dict):
            return value
        bad = self._FORBIDDEN_CONFIG_KEYS & {str(k).lower() for k in value.keys()}
        if bad:
            raise serializers.ValidationError(
                 f"Node.config must reference credentials by ID, not raw values. "
                 f"Forbidden structural configuration keys detected: {sorted(bad)}"
             )
        return value


class EdgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edge
        fields = ("id", "workflow", "source", "target", "created_at")
        read_only_fields = ("id", "created_at")

    def validate(self, attrs: dict) -> dict:
        request = self.context.get("request")
        user = request.user if request else None
        workflow = attrs.get("workflow")
        source = attrs.get("source")
        target = attrs.get("target")

        # All three objects must belong to the caller's scope.
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")
        for obj, label in ((workflow, "workflow"), (source, "source"), (target, "target")):
            if obj is None or obj.user_id != user.id:
                raise serializers.ValidationError({label: "Invalid object."})
        if workflow.id not in (source.workflow_id, target.workflow_id):
            raise serializers.ValidationError("Endpoints must share the workflow.")
        return attrs


class WorkflowRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowRun
        fields = (
            "id", "workflow", "status", "started_at", "finished_at", "created_at",
        )
        read_only_fields = ("id", "status", "started_at", "finished_at", "created_at")

    def validate_workflow(self, workflow: Workflow) -> Workflow:
        request = self.context.get("request")
        if request is None or workflow.user_id != request.user.id:
            raise serializers.ValidationError("Invalid workflow.")
        return workflow
