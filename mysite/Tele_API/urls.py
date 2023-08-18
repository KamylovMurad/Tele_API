from django.urls import path
from .views import (
  VerifyCodeView,
  SendVerificationView,
  UserProfileView,
)

app_name = "Tele_API"

urlpatterns = [
    path('Send Code/', SendVerificationView.as_view(), name='send_verification'),
    path('Verify Code/', VerifyCodeView.as_view(), name='verify_code'),
    path('Profile/<str:phone_number>/', UserProfileView.as_view(), name='user_profile'),
]