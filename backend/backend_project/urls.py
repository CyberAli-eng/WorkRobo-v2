"""Project URL routing."""
from django.contrib import admin
from django.urls import include, path

from hello.views import hello_world

urlpatterns = [
    path("admin/", admin.site.urls),
    # Public probe — used by the frontend to verify the bridge.
    path("api/hello/", hello_world, name="hello_world"),
    # Auth (register, login, refresh, logout, me).
    path("api/auth/", include("accounts.urls")),
    #Core urls (DRF router, user-scoped).
    path("api/", include("core.urls")),
    # Workflows (DRF router, user-scoped).
    path("api/", include("workflows.urls")),

]
