"""
Abstract base for any model whose rows are owned by a single user.

Concrete models inherit this and gain a ``user`` FK plus the
``UserScopedManager`` — they MUST use ``UserScopedManager.objects``
in place of the default ``models.Manager()`` for the scoping guarantee
to hold.
"""
from django.conf import settings
from django.db import models

from .managers import UserScopedManager


class UserScopedModel(models.Model):
    """Abstract base. Add per-user data on top of this."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="+",
        related_query_name="+",
    )

    objects = UserScopedManager()

    class Meta:
        abstract = True
