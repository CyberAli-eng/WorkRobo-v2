from django.contrib import admin

from .models import Edge, Node, Workflow, WorkflowRun


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "updated_at")
    list_filter = ("user",)
    search_fields = ("name", "description", "user__email")


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ("id", "workflow", "kind", "user")
    list_filter = ("kind", "user")


@admin.register(Edge)
class EdgeAdmin(admin.ModelAdmin):
    list_display = ("id", "workflow", "source", "target", "user")
    list_filter = ("user",)


@admin.register(WorkflowRun)
class WorkflowRunAdmin(admin.ModelAdmin):
    list_display = ("id", "workflow", "status", "started_at", "finished_at", "user")
    list_filter = ("status", "user")
