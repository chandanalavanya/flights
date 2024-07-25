from django.urls import path
from .views import RegisterView, RenewAccessTokenView, LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('renew-token/', RenewAccessTokenView.as_view(), name='renew_token'),
    path('login/', LoginView.as_view(), name='login'),
]