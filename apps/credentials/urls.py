"""
URL configuration for credentials app
"""
from django.urls import path
from .views import (
    CredentialListView, CredentialDetailView, CredentialCreateView,
    CredentialRevokeView, CredentialVerifyView, CredentialShareCreateView,
    CredentialShareVerifyView, CredentialBatchListView, BlockchainTransactionListView,
    CredentialQRCodeView
)

urlpatterns = [
    # Credentials
    path('', CredentialListView.as_view(), name='credential_list'),
    path('issue/', CredentialCreateView.as_view(), name='credential_create'),
    path('<uuid:id>/', CredentialDetailView.as_view(), name='credential_detail'),
    path('<uuid:id>/revoke/', CredentialRevokeView.as_view(), name='credential_revoke'),
    
    # Verification
    path('verify/<str:credential_id>/', CredentialVerifyView.as_view(), name='credential_verify_by_id'),
    path('verify/', CredentialVerifyView.as_view(), name='credential_verify'),
    
    # Sharing
    path('share/', CredentialShareCreateView.as_view(), name='credential_share'),
    path('share/<str:token>/', CredentialShareVerifyView.as_view(), name='credential_share_verify'),
    
    # QR Code
    path('<uuid:credential_id>/qr/', CredentialQRCodeView.as_view(), name='credential_qr_code'),
    
    # Batches
    path('batches/', CredentialBatchListView.as_view(), name='batch_list'),
    
    # Blockchain
    path('transactions/', BlockchainTransactionListView.as_view(), name='transaction_list'),
]
