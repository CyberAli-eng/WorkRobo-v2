"""
User-scoped manager and queryset.

These are the security primitive of the project. Every model that holds
per-user data inherits ``UserScopedModel`` and exposes ``UserScopedManager``,
which only knows how to return rows for an explicit user via ``for_user(...)``.

Why this matters: if a view forgets to filter by user but uses the manager
(e.g. ``Model.objects.for_user(request.user).get(pk=...)``), the queryset
is already pre-filtered and ``DoesNotExist`` is raised for another user's
row. The bypass path is the bare ``Model._default_manager.all()`` (used
by admin and management commands) — and that is the only place it should
appear.
"""
from django.db import models


class UserScopedQuerySet(models.QuerySet):
    """A queryset pre-filtered to a single user at the chain's root."""

    def for_user(self, user):
        """Return only rows owned by ``user``.

        ``user`` is the authenticated request user; it may be an
        ``AnonymousUser`` in which case the returned queryset is empty
        (caller is expected to handle auth via DRF permissions).
        """
        if user is None or not getattr(user, "is_authenticated", False):
            return self.none()
        return self.filter(user=user)


class UserScopedManager(models.Manager.from_queryset(UserScopedQuerySet)):
    """Default manager for user-scoped models.

    Note: ``get_queryset()`` is intentionally NOT overridden to auto-apply
    a user filter — that would require threading the request user into the
    manager (anti-pattern). The contract is: every view calls
    ``for_user(request.user)`` explicitly. Doing so makes the scoping
    visible in the view code rather than magic.
    """
