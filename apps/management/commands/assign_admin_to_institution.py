"""
Management command to assign an institution admin user to an institution
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User, InstitutionAdminProfile, UserRole
from apps.institutions.models import Institution


class Command(BaseCommand):
    help = 'Assign an institution admin user to an institution'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@gmail.com',
            help='Email of the user to assign (default: admin@gmail.com)',
        )
        parser.add_argument(
            '--institution',
            type=str,
            help='Institution name or ID to assign the user to. If not provided, uses the first institution.',
        )
        parser.add_argument(
            '--position',
            type=str,
            default='Institution Administrator',
            help='Position title for the admin (default: Institution Administrator)',
        )
        parser.add_argument(
            '--department',
            type=str,
            default='',
            help='Department for the admin',
        )
        parser.add_argument(
            '--employee-id',
            type=str,
            default='',
            help='Employee ID for the admin',
        )

    def handle(self, *args, **options):
        email = options['email']
        institution_name = options.get('institution')
        position = options.get('position', 'Institution Administrator')
        department = options.get('department', '')
        employee_id = options.get('employee_id', '')
        
        # Get user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with email "{email}" not found'))
            return
        
        # Get or find institution
        institution = None
        if institution_name:
            # Try exact match first, then contains, then by ID
            institution = Institution.objects.filter(name__iexact=institution_name).first()
            if not institution:
                institution = Institution.objects.filter(name__icontains=institution_name).first()
            if not institution:
                try:
                    institution = Institution.objects.get(id=institution_name)
                except (Institution.DoesNotExist, ValueError):
                    pass
        
        # If no institution specified or found, use the first one
        if not institution:
            institution = Institution.objects.first()
            if not institution:
                self.stdout.write(self.style.ERROR('No institution found. Please create an institution first.'))
                return
        
        # Update user role to institution_admin if not already
        if user.role != UserRole.INSTITUTION_ADMIN:
            user.role = UserRole.INSTITUTION_ADMIN
            user.save(update_fields=['role'])
            self.stdout.write(self.style.WARNING(f'Updated user role to Institution Admin'))
        
        # Create or update InstitutionAdminProfile
        admin_profile, created = InstitutionAdminProfile.objects.get_or_create(
            user=user,
            defaults={
                'institution': institution,
                'position': position,
                'department': department,
                'employee_id': employee_id,
            }
        )
        
        if not created:
            # Update existing profile
            admin_profile.institution = institution
            if position:
                admin_profile.position = position
            if department:
                admin_profile.department = department
            if employee_id:
                admin_profile.employee_id = employee_id
            admin_profile.save()
            self.stdout.write(self.style.SUCCESS(
                f'Updated InstitutionAdminProfile for {user.email} to institution "{institution.name}"'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Created InstitutionAdminProfile for {user.email} and assigned to institution "{institution.name}"'
            ))
        
        # Display summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Assignment Summary:'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'User: {user.email} ({user.full_name})')
        self.stdout.write(f'Role: {user.get_role_display()}')
        self.stdout.write(f'Institution: {institution.name}')
        self.stdout.write(f'Position: {admin_profile.position or "Not set"}')
        self.stdout.write(f'Department: {admin_profile.department or "Not set"}')
        self.stdout.write(f'Employee ID: {admin_profile.employee_id or "Not set"}')
        self.stdout.write(self.style.SUCCESS('='*60))

