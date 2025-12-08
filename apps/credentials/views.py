"""
Views for credentials
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
import uuid

from .models import Credential, CredentialStatus, CredentialShare, CredentialBatch, BlockchainTransaction
from .serializers import (
    CredentialListSerializer, CredentialDetailSerializer,
    CredentialCreateSerializer, CredentialVerifySerializer,
    CredentialShareSerializer, CredentialBatchSerializer,
    BlockchainTransactionSerializer
)
from apps.accounts.permissions import (
    IsSuperAdmin, IsSuperAdminOrInstitutionAdmin, IsStudent,
    CanIssueCredentials, CanRevokeCredentials, CanVerifyCredentials
)
from apps.accounts.models import UserRole, ActivityLog


class CredentialListView(generics.ListAPIView):
    """List credentials based on user role"""
    serializer_class = CredentialListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'credential_type', 'institution']
    search_fields = ['credential_id', 'holder_name', 'program_name']
    ordering_fields = ['created_at', 'issue_date']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == UserRole.SUPER_ADMIN:
            return Credential.objects.all()
        elif user.role == UserRole.INSTITUTION_ADMIN:
            try:
                institution = user.institution_admin_profile.institution
                return Credential.objects.filter(institution=institution)
            except:
                return Credential.objects.none()
        elif user.role == UserRole.STUDENT:
            return Credential.objects.filter(holder=user)
        
        return Credential.objects.none()


class CredentialDetailView(generics.RetrieveAPIView):
    """Get credential details"""
    serializer_class = CredentialDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == UserRole.SUPER_ADMIN:
            return Credential.objects.all()
        elif user.role == UserRole.INSTITUTION_ADMIN:
            try:
                institution = user.institution_admin_profile.institution
                return Credential.objects.filter(institution=institution)
            except:
                return Credential.objects.none()
        elif user.role == UserRole.STUDENT:
            return Credential.objects.filter(holder=user)
        
        return Credential.objects.none()


class CredentialCreateView(generics.CreateAPIView):
    """Issue a new credential"""
    serializer_class = CredentialCreateSerializer
    permission_classes = [CanIssueCredentials]
    
    def perform_create(self, serializer):
        credential = serializer.save(
            issued_by=self.request.user,
            status=CredentialStatus.ISSUED,
            issue_date=timezone.now().date()
        )
        
        # Log activity
        ActivityLog.objects.create(
            user=self.request.user,
            action=ActivityLog.ActionType.CREDENTIAL_ISSUED,
            description=f"Issued credential {credential.credential_id} to {credential.holder_name}",
            metadata={'credential_id': str(credential.id)}
        )


class CredentialRevokeView(APIView):
    """Revoke a credential"""
    permission_classes = [CanRevokeCredentials]
    
    def post(self, request, id):
        credential = get_object_or_404(Credential, id=id)
        
        if credential.status == CredentialStatus.REVOKED:
            return Response(
                {'error': 'Credential is already revoked'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        
        credential.status = CredentialStatus.REVOKED
        credential.revoked_at = timezone.now()
        credential.revoked_by = request.user
        credential.revocation_reason = reason
        credential.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action=ActivityLog.ActionType.CREDENTIAL_REVOKED,
            description=f"Revoked credential {credential.credential_id}",
            metadata={'credential_id': str(credential.id), 'reason': reason}
        )
        
        return Response({'message': 'Credential revoked successfully'})


class CredentialVerifyView(APIView):
    """Verify a credential"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, credential_id=None):
        """GET request - Display verification result in HTML"""
        from django.shortcuts import render
        from apps.verifications.models import VerificationLog, VerificationMethod, VerificationResult
        
        # Get credential_id from URL or query parameter
        credential_id = credential_id or request.GET.get('credential_id')
        
        if not credential_id:
            return render(request, 'credentials/verify.html', {
                'error': 'Credential ID is required',
                'credential_id': ''
            }, status=400)
        
        # Strip whitespace
        credential_id = credential_id.strip()
        
        try:
            # Try case-insensitive lookup first
            try:
                credential = Credential.objects.select_related('institution', 'holder').get(credential_id__iexact=credential_id)
            except Credential.DoesNotExist:
                # Fallback to exact match (case-sensitive)
                credential = Credential.objects.select_related('institution', 'holder').get(credential_id=credential_id)
            
            # Log verification
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Determine verification method
            method = VerificationMethod.SHARE_LINK if 'share' in request.path else VerificationMethod.CREDENTIAL_ID
            
            # Determine result
            if credential.status == CredentialStatus.ISSUED:
                result = VerificationResult.VALID
            elif credential.status == CredentialStatus.REVOKED:
                result = VerificationResult.REVOKED
            elif credential.status == CredentialStatus.EXPIRED:
                result = VerificationResult.EXPIRED
            else:
                result = VerificationResult.INVALID
            
            # Create verification log
            VerificationLog.objects.create(
                credential=credential,
                credential_id_searched=credential_id,
                verifier=request.user if request.user.is_authenticated else None,
                verifier_email=request.user.email if request.user.is_authenticated else '',
                method=method,
                result=result,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Prepare context
            context = {
                'credential': credential,
                'is_valid': credential.status == CredentialStatus.ISSUED,
                'status': credential.status,
                'credential_id': credential_id,
            }
            
            return render(request, 'credentials/verify.html', context)
            
        except Credential.DoesNotExist:
            # Log failed verification
            ip_address = self._get_client_ip(request)
            VerificationLog.objects.create(
                credential_id_searched=credential_id,
                method=VerificationMethod.CREDENTIAL_ID,
                result=VerificationResult.NOT_FOUND,
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return render(request, 'credentials/verify.html', {
                'error': 'Credential not found',
                'credential_id': credential_id
            }, status=404)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error verifying credential: {str(e)}", exc_info=True)
            
            return render(request, 'credentials/verify.html', {
                'error': f'Error verifying credential: {str(e)}',
                'credential_id': credential_id
            }, status=500)
    
    def post(self, request, credential_id=None):
        """POST request - API verification"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Log incoming request data for debugging
        logger.info(f"Incoming request data: {request.data}")
        logger.info(f"Request data type: {type(request.data)}")
        
        try:
            serializer = CredentialVerifySerializer(data=request.data)
            if not serializer.is_valid():
                logger.error(f"Serializer validation errors: {serializer.errors}")
                return Response({
                    'valid': False,
                    'error': 'Invalid request data',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Serializer validation error: {str(e)}", exc_info=True)
            return Response({
                'valid': False,
                'error': f'Invalid request data: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get validated data
        validated_data = serializer.validated_data
        credential_id = credential_id or validated_data.get('credential_id')
        blockchain_hash = validated_data.get('blockchain_hash')
        
        logger.info(f"After validation - credential_id: '{credential_id}', blockchain_hash: '{blockchain_hash}'")
        
        # Clean inputs once
        if credential_id:
            credential_id = str(credential_id).strip()
            credential_id = ''.join(c for c in credential_id if c.isprintable())
        if blockchain_hash:
            blockchain_hash = str(blockchain_hash).strip()
            blockchain_hash = ''.join(c for c in blockchain_hash if c.isprintable())
        
        logger.info(f"Looking up - credential_id: '{credential_id}', blockchain_hash: '{blockchain_hash}'")
        
        try:
            if credential_id:
                # SIMPLE LOOKUP - use filter().first() instead of get()
                credential = Credential.objects.filter(credential_id__iexact=credential_id).first()
                
                if not credential:
                    credential = Credential.objects.filter(credential_id=credential_id).first()
                
                if not credential:
                    sample = list(Credential.objects.values_list('credential_id', flat=True)[:5])
                    logger.error(f"NOT FOUND! Searched: '{credential_id}' | DB has: {sample}")
                    raise Credential.DoesNotExist()
            elif blockchain_hash:
                credential = Credential.objects.get(blockchain_hash=blockchain_hash)
            else:
                return Response({
                    'valid': False,
                    'error': 'Either credential_id or blockchain_hash is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Log verification if user is authenticated
            if request.user.is_authenticated:
                ActivityLog.objects.create(
                    user=request.user,
                    action=ActivityLog.ActionType.CREDENTIAL_VERIFIED,
                    description=f"Verified credential {credential.credential_id}",
                    metadata={'credential_id': str(credential.id)}
                )
                
                # Update employer verification count
                if request.user.role == UserRole.EMPLOYER:
                    try:
                        profile = request.user.employer_profile
                        profile.verifications_this_month += 1
                        profile.save()
                    except:
                        pass
            
            # Prepare response based on status
            is_valid = credential.status == CredentialStatus.ISSUED
            
            response_data = {
                'valid': is_valid,
                'status': credential.status,
                'credential': {
                    'credential_id': credential.credential_id,
                    'credential_type': credential.credential_type,
                    'holder_name': credential.holder_name,
                    'holder_student_id': credential.holder_student_id,
                    'holder_date_of_birth': credential.holder_date_of_birth.isoformat() if credential.holder_date_of_birth else None,
                    'institution': credential.institution.name if credential.institution else None,
                    'program_name': credential.program_name,
                    'degree_level': credential.degree_level,
                    'major': credential.major,
                    'minor': credential.minor,
                    'specialization': credential.specialization,
                    'grade': credential.grade,
                    'honors': credential.honors,
                    'credits_earned': str(credential.credits_earned) if credential.credits_earned else None,
                    'enrollment_date': credential.enrollment_date.isoformat() if credential.enrollment_date else None,
                    'completion_date': credential.completion_date.isoformat() if credential.completion_date else None,
                    'issue_date': credential.issue_date.isoformat() if credential.issue_date else None,
                    'expiry_date': credential.expiry_date.isoformat() if credential.expiry_date else None,
                    'blockchain_hash': credential.blockchain_hash,
                    'blockchain_tx_id': credential.blockchain_tx_id,
                    'block_number': credential.block_number,
                    'ipfs_hash': credential.ipfs_hash,
                },
                'institution': {
                    'name': credential.institution.name if credential.institution else None,
                    'country': credential.institution.country if credential.institution else None,
                    'accreditation_status': credential.institution.accreditation_status if credential.institution else None,
                    'is_partner': credential.institution.is_partner if credential.institution else False,
                    'is_verified': credential.institution.is_verified if credential.institution else False,
                }
            }
            
            if credential.status == CredentialStatus.REVOKED:
                response_data['revocation'] = {
                    'revoked_at': credential.revoked_at.isoformat() if credential.revoked_at else None,
                    'reason': credential.revocation_reason,
                }
            
            return Response(response_data)
            
        except Credential.DoesNotExist:
            # Log the attempted lookup for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Credential not found - ID: {credential_id}, Hash: {blockchain_hash}")
            
            # Create verification log for not found credential
            if request.user.is_authenticated:
                try:
                    from apps.verifications.models import VerificationLog, VerificationMethod, VerificationResult
                    ip_address = self._get_client_ip(request)
                    user_agent = request.META.get('HTTP_USER_AGENT', '')
                    
                    VerificationLog.objects.create(
                        credential=None,
                        credential_id_searched=credential_id or blockchain_hash,
                        method=VerificationMethod.CREDENTIAL_ID if credential_id else VerificationMethod.BLOCKCHAIN_HASH,
                        result=VerificationResult.NOT_FOUND,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        verifier=request.user,
                        verifier_email=request.user.email if request.user.is_authenticated else '',
                    )
                except Exception as e:
                    logger.error(f"Error creating verification log: {str(e)}")
            
            return Response({
                'valid': False,
                'status': 'not_found',
                'error': f'Credential not found in the system',
                'message': f'The credential ID "{credential_id or blockchain_hash}" does not exist in our database.',
                'searched_id': credential_id,
                'searched_hash': blockchain_hash
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Log unexpected errors
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error verifying credential: {str(e)}", exc_info=True)
            
            return Response({
                'valid': False,
                'error': f'An error occurred while verifying the credential: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CredentialShareCreateView(generics.CreateAPIView):
    """Create a share link for a credential"""
    serializer_class = CredentialShareSerializer
    permission_classes = [IsStudent]
    
    def check_permissions(self, request):
        """Override to return JSON errors instead of HTML redirects"""
        if not request.user or not request.user.is_authenticated:
            raise permissions.PermissionDenied('Authentication required')
        
        if request.user.role != UserRole.STUDENT:
            raise permissions.PermissionDenied('Only students can share credentials')
        
        # Call parent to check other permissions
        super().check_permissions(request)
    
    def handle_exception(self, exc):
        """Override to ensure all exceptions return JSON"""
        if isinstance(exc, permissions.PermissionDenied):
            return Response({
                'error': str(exc),
                'detail': 'Permission denied. Only students can share credentials.'
            }, status=status.HTTP_403_FORBIDDEN)
        return super().handle_exception(exc)
    
    def create(self, request, *args, **kwargs):
        """Override create to handle errors properly and return JSON"""
        try:
            # Ensure request is parsed as JSON
            if hasattr(request, 'data'):
                serializer = self.get_serializer(data=request.data)
            else:
                import json
                body = request.body.decode('utf-8')
                data = json.loads(body) if body else {}
                serializer = self.get_serializer(data=data)
            
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except permissions.PermissionDenied as e:
            return Response({
                'error': str(e),
                'detail': 'Permission denied. You can only share your own credentials.'
            }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating credential share: {str(e)}", exc_info=True)
            error_detail = str(e)
            if hasattr(e, 'detail'):
                error_detail = e.detail
            elif hasattr(e, 'messages'):
                error_detail = ', '.join(e.messages)
            return Response({
                'error': error_detail,
                'detail': 'Failed to create share link. Please try again.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        credential = serializer.validated_data['credential']
        
        # Verify the student owns this credential
        if credential.holder != self.request.user:
            raise permissions.PermissionDenied('You can only share your own credentials')
        
        # Generate unique share token
        share_token = str(uuid.uuid4().hex)
        
        # Save the share
        share = serializer.save(share_token=share_token)
        
        # Send email if shared_with_email is provided
        if share.shared_with_email:
            try:
                self._send_share_email(share, credential)
            except Exception as e:
                # Log error but don't fail the request
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send share email: {str(e)}")
    
    def _send_share_email(self, share, credential):
        """Send email notification about shared credential"""
        from django.template.loader import get_template
        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings
        from apps.home.models import GeneralSettings
        
        # Get site settings
        site_settings = GeneralSettings.objects.first()
        site_name = site_settings.site_name if site_settings else 'CertChain'
        
        # Build share URL
        share_url = f"{self.request.scheme}://{self.request.get_host()}/credentials/share/{share.share_token}/"
        
        # Prepare email context
        context = {
            'share': share,
            'credential': credential,
            'share_url': share_url,
            'holder_name': credential.holder.full_name if credential.holder else credential.holder_name,
            'institution_name': credential.institution.name if credential.institution else 'Unknown Institution',
            'program_name': credential.program_name or 'N/A',
            'expires_at': share.expires_at,
            'settings': site_settings,
            'request': self.request,
        }
        
        # Render email template
        try:
            template = get_template('credentials/emails/credential_share.html')
            html_content = template.render(context)
        except Exception as e:
            # Fallback template if custom template doesn't exist
            html_content = f"""
            <html>
            <body>
                <h2>Credential Shared with You</h2>
                <p>Hello,</p>
                <p>{context['holder_name']} has shared a credential with you.</p>
                <p><strong>Institution:</strong> {context['institution_name']}</p>
                <p><strong>Program:</strong> {context['program_name']}</p>
                <p>View the credential: <a href="{share_url}">{share_url}</a></p>
                {f'<p><strong>Expires:</strong> {share.expires_at.strftime("%B %d, %Y")}</p>' if share.expires_at else ''}
                <p>Best regards,<br>{site_name} Team</p>
            </body>
            </html>
            """
        
        # Create and send email
        subject = f'{site_name} - Credential Shared with You'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = share.shared_with_email
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"View the shared credential: {share_url}",  # Plain text fallback
            from_email=from_email,
            to=[to_email],
        )
        
        email.attach_alternative(html_content, "text/html")
        email.send()


class CredentialQRCodeView(APIView):
    """Generate or retrieve QR code for a credential"""
    permission_classes = [IsStudent]
    
    def get(self, request, credential_id):
        """Get QR code for a credential, generate if not exists"""
        try:
            credential = Credential.objects.get(id=credential_id)
            
            # Verify the student owns this credential
            if credential.holder != request.user:
                return Response({
                    'error': 'Permission denied. You can only view QR codes for your own credentials.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Always regenerate verification URL using current request host (not stored one)
            current_verification_url = credential.get_verification_url(request=request)
            
            # Check if stored verification_url is outdated (e.g., has example.com)
            needs_qr_regeneration = (
                not credential.qr_code or 
                credential.verification_url != current_verification_url or
                'example.com' in (credential.verification_url or '')
            )
            
            # Update stored verification_url to use current host
            if credential.verification_url != current_verification_url:
                credential.verification_url = current_verification_url
                if not needs_qr_regeneration:
                    # Only save verification_url if we're not regenerating QR (to avoid double save)
                    credential.save(update_fields=['verification_url'])
            
            # Generate/regenerate QR code if needed (always uses current verification URL)
            if needs_qr_regeneration:
                credential.generate_qr_code(save=True, request=request)
                # Don't fail if QR generation fails - client will use fallback
            
            # Return QR code URL and verification URL (always use current request host)
            return Response({
                'qr_code_url': credential.qr_code.url if credential.qr_code else None,
                'verification_url': current_verification_url,  # Always use current request host
                'credential_id': credential.credential_id
            })
            
        except Credential.DoesNotExist:
            return Response({
                'error': 'Credential not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating QR code: {str(e)}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CredentialShareVerifyView(APIView):
    """Verify credential via share token"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, token):
        try:
            share = CredentialShare.objects.get(share_token=token)
            
            if not share.is_valid():
                return Response({
                    'valid': False,
                    'error': 'Share link has expired or reached maximum views'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Increment view count
            share.view_count += 1
            share.save()
            
            credential = share.credential
            
            response_data = {
                'valid': credential.status == CredentialStatus.ISSUED,
                'status': credential.status,
                'credential': {
                    'credential_id': credential.credential_id,
                    'holder_name': credential.holder_name,
                    'institution': credential.institution.name,
                    'program_name': credential.program_name,
                    'degree_level': credential.degree_level,
                    'completion_date': credential.completion_date,
                    'issue_date': credential.issue_date,
                }
            }
            
            # Apply privacy settings
            if not share.hide_grade:
                response_data['credential']['grade'] = credential.grade
            if not share.hide_student_id:
                response_data['credential']['student_id'] = credential.holder_student_id
            
            return Response(response_data)
            
        except CredentialShare.DoesNotExist:
            return Response({
                'valid': False,
                'error': 'Invalid share link'
            }, status=status.HTTP_404_NOT_FOUND)


class CredentialBatchListView(generics.ListCreateAPIView):
    """List or create credential batches"""
    serializer_class = CredentialBatchSerializer
    permission_classes = [IsSuperAdminOrInstitutionAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return CredentialBatch.objects.all()
        try:
            institution = user.institution_admin_profile.institution
            return CredentialBatch.objects.filter(institution=institution)
        except:
            return CredentialBatch.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class BlockchainTransactionListView(generics.ListAPIView):
    """List blockchain transactions"""
    serializer_class = BlockchainTransactionSerializer
    permission_classes = [IsSuperAdminOrInstitutionAdmin]
    filterset_fields = ['transaction_type', 'is_confirmed']
    
    def get_queryset(self):
        return BlockchainTransaction.objects.select_related('credential')
