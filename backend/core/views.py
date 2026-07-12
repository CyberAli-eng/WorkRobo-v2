from rest_framework import viewsets
from .models import Credential
from .serializers import CredentialCreateSerializer, CredentialSerializer

class _UserScopedViewSet(viewsets.ModelViewSet):
    """Mixin: locks the queryset to the request user and stamps user on create."""

    def get_queryset(self):
        return self.queryset.for_user(self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CredentialViewSet(_UserScopedViewSet):
    queryset = Credential.objects.all()
    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return CredentialCreateSerializer
        return CredentialSerializer