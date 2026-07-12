from rest_framework.routers import DefaultRouter
from .views import CredentialViewSet

router = DefaultRouter()
router.register(r"credentials", CredentialViewSet, basename="credential")
urlpatterns = router.urls