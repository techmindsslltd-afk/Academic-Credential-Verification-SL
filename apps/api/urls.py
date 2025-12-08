
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from apps.api.views import *
from . import views

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [  

    path('api/applicationpins/', ApplicationPinList.as_view(), name='applicationpin-list'),
    path('api/applicationpins/<int:pk>/', ApplicationPinDetail.as_view(), name='applicationpin-detail'),

    path('api/jitsi-token/', JitsiTokenView.as_view(), name='jitsi_token'),  # Map the URL to the view

    path('api/fee-payments/', FeePaymentList.as_view(), name='fee_payment_list'),
    path('api/fee-payments/<int:pk>/', FeePaymentDetail.as_view(), name='fee_payment_detail'),

    
    #path('api-token-auth/', obtain_auth_token, name='api_token_auth'),

    path('api/login/', LoginView.as_view(), name='api-login'),
    path('api/logout/', LogoutView.as_view(), name='api-logout'),
]
