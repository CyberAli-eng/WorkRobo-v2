"""
Abstract base for any model whose rows are owned by a single user.

Concrete models inherit this and gain a ``user`` FK plus the
``UserScopedManager`` — they MUST use ``UserScopedManager.objects``
in place of the default ``models.Manager()`` for the scoping guarantee
to hold.
"""
# backend/core/models.py
from django.db import models
from django.conf import settings
from core.crypto import encrypt, decrypt
from .managers import UserScopedManager # Ensuring our isolated manager is here

class UserScopedModel(models.Model):
    """
    Your original UserScopedModel declaration lives here.
    Make sure all of its fields and methods are indented under this block.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    objects = UserScopedManager()

    class Meta:
        abstract = True


# 🔴 MOVE THIS OUT TO THE TOP LEVEL (Flush against the left margin)
class Credential(UserScopedModel):
    PROVIDER_CHOICES = [
        ("openai", "OpenAI"),
        ("anthropic", "Anthropic"),
        ("github", "GitHub"),
        ("slack", "Slack"),
        ("http", "Generic HTTP"),
        ("smtp", "SMTP"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=200)
    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES)
    encrypted_value = models.TextField()  # Stores base64 Fernet token ciphertext string
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def set_value(self, plaintext: str) -> None:
        """Encrypts data instantly and attaches the token signature string to the database column."""
        self.encrypted_value = encrypt(plaintext)

    def get_value(self) -> str:
        """Decrypts row token data directly back into operational working memory contexts."""
        return decrypt(self.encrypted_value)

    def __str__(self):
        return f"{self.name} ({self.get_provider_display()})"