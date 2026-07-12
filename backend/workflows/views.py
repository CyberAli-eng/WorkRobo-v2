"""
Viewsets that scope every read/write to the request user.

``get_queryset`` returns ``Model.objects.for_user(self.request.user)`` —
this is the only path data leaves the database, so a user can never
reach another user's rows even by guessing IDs (the manager's queryset
is pre-filtered and ``get(...)`` raises ``DoesNotExist``).

``perform_create`` stamps ``user=request.user`` on every new row so
clients cannot write ``user`` into the body.
"""
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Edge, Node, Workflow, WorkflowRun
from .serializers import (
    EdgeSerializer,
    NodeSerializer,
    WorkflowRunSerializer,
    WorkflowSerializer,
)


class _UserScopedViewSet(viewsets.ModelViewSet):
    """Mixin: locks the queryset to the request user and stamps user on create."""

    def get_queryset(self):
        return self.queryset.for_user(self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WorkflowViewSet(_UserScopedViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer

    @action(detail=True, methods=["get"], url_path="nodes")
    def nodes(self, request, pk=None):
        workflow = self.get_object()  # already scoped to request user
        nodes = Node.objects.for_user(request.user).filter(workflow=workflow)
        return Response(NodeSerializer(nodes, many=True).data)

    @action(detail=True, methods=["get"], url_path="edges")
    def edges(self, request, pk=None):
        workflow = self.get_object()
        edges = Edge.objects.for_user(request.user).filter(workflow=workflow)
        return Response(EdgeSerializer(edges, many=True).data)

    @action(detail=True, methods=["get", "post"], url_path="runs")
    def runs(self, request, pk=None):
        workflow = self.get_object()
        if request.method == "GET":
            runs = WorkflowRun.objects.for_user(request.user).filter(workflow=workflow)
            return Response(WorkflowRunSerializer(runs, many=True).data)
        # POST — create a new run for this workflow.
        serializer = WorkflowRunSerializer(
            data={"workflow": workflow.id}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, status="pending")
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NodeViewSet(_UserScopedViewSet):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer


class EdgeViewSet(_UserScopedViewSet):
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer


class WorkflowRunViewSet(_UserScopedViewSet):
    queryset = WorkflowRun.objects.all()
    serializer_class = WorkflowRunSerializer
    http_method_names = ["get", "delete", "head", "options"]  # runs are POSTed via /workflows/<id>/runs/
