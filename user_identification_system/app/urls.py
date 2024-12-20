from django.urls import path, include
from .routers import router
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('verify-email/', VerifyUserEmail.as_view(), name='verify'),
    path('resend-otp/', ResendOtpView.as_view(), name='resend-otp'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('profile/', TestAuthenticationView.as_view(), name='granted'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh-token'),
    # path('logout/', LogoutUserView.as_view(), name='logout'),
     
    # all paths from router
    path('', include(router.urls)),
    
    # user activate and deactivate paths
    path('users/<uuid:id>/activate', UserViewSet.as_view({"get": "activate_user"}), name='user-activate'),
    path('users/<uuid:id>/deactivate', UserViewSet.as_view({"get": "deactivate_user"}), name='user-deactivate'),
    
]