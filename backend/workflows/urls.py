"""DRF router for the workflow domain — mounted at /api/workflows/."""
from rest_framework.routers import DefaultRouter

from .views import EdgeViewSet, NodeViewSet, WorkflowRunViewSet, WorkflowViewSet

router = DefaultRouter()
router.register(r"workflows", WorkflowViewSet, basename="workflow")
router.register(r"nodes", NodeViewSet, basename="node")
router.register(r"edges", EdgeViewSet, basename="edge")
router.register(r"runs", WorkflowRunViewSet, basename="run")

urlpatterns = router.urls
