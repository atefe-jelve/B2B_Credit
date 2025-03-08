from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', obtain_auth_token),
]
