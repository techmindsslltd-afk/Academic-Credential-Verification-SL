"""
Management command to assign a credential to a user
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User, StudentProfile, UserRole
from apps.credentials.models import Credential


class Command(BaseCommand):
    help = 'Assign a credential to a user by credential ID and user email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--credential-id',
            type=str,
            required=True,
            help='Credential ID (e.g., CERT-2025-SL-40CBD7)',
        )
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email of the user to assign the credential to',
        )
        parser.add_argument(
            '--update-role',
            action='store_true',
            help='Update user role to student if not already',
        )

    def handle(self, *args, **options):
        credential_id = options['credential_id']
        email = options['email']
        update_role = options.get('update_role', False)
        
        # Get credential
        try:
            credential = Credential.objects.get(credential_id=credential_id)
        except Credential.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Credential with ID "{credential_id}" not found'))
            return
        except Credential.MultipleObjectsReturned:
            self.stdout.write(self.style.ERROR(f'Multiple credentials found with ID "{credential_id}"'))
            return
        
        # Get user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with email "{email}" not found'))
            return
        
        # Update user role to student if requested
        if update_role and user.role != UserRole.STUDENT:
            user.role = UserRole.STUDENT
            user.save(update_fields=['role'])
            self.stdout.write(self.style.WARNING(f'Updated user role to Student'))
        
        # Create or update StudentProfile if needed
        student_profile, created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'student_id': credential.holder_student_id or '',
                'date_of_birth': credential.holder_date_of_birth,
                'institution': credential.institution,
            }
        )
        
        if not created:
            # Update existing profile if needed
            if not student_profile.student_id and credential.holder_student_id:
                student_profile.student_id = credential.holder_student_id
            if not student_profile.date_of_birth and credential.holder_date_of_birth:
                student_profile.date_of_birth = credential.holder_date_of_birth
            if not student_profile.institution and credential.institution:
                student_profile.institution = credential.institution
            student_profile.save()
        
        # Update credential holder
        old_holder = credential.holder
        credential.holder = user
        credential.holder_name = user.full_name
        credential.save(update_fields=['holder', 'holder_name'])
        
        # Display summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Credential Assignment Summary:'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Credential ID: {credential.credential_id}')
        self.stdout.write(f'Credential Type: {credential.get_credential_type_display()}')
        self.stdout.write(f'Status: {credential.get_status_display()}')
        self.stdout.write(f'Previous Holder: {old_holder.email} ({old_holder.full_name})')
        self.stdout.write(f'New Holder: {user.email} ({user.full_name})')
        self.stdout.write(f'User Role: {user.get_role_display()}')
        self.stdout.write(f'Institution: {credential.institution.name if credential.institution else "N/A"}')
        self.stdout.write(f'Program: {credential.program_name}')
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully assigned credential {credential_id} to {email}'))

