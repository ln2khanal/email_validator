from rest_framework.routers import DefaultRouter
from .apis import ValidateEmailsCheckedListAPI

router = DefaultRouter()
router.register(r'emails', ValidateEmailsCheckedListAPI, basename='emails-checked-list')

urlpatterns = router.urls