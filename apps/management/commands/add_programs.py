"""
Management command to add programs to an institution
"""
from django.core.management.base import BaseCommand
from apps.institutions.models import Institution, Program


class Command(BaseCommand):
    help = 'Add programs to an institution'

    def add_arguments(self, parser):
        parser.add_argument(
            '--institution',
            type=str,
            help='Institution name or ID. If not provided, uses the first institution.',
        )

    def handle(self, *args, **options):
        institution_name = options.get('institution')
        
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
        
        self.stdout.write(f'Adding programs to: {institution.name}')
        
        # Define programs to add
        programs_to_add = [
            {
                'name': 'Information Technology',
                'code': 'IT',
                'degree_level': Program.DegreeLevel.BACHELOR,
                'department': 'Computer Science',
                'faculty': 'Science and Technology',
                'duration_years': 4.0,
                'is_active': True,
            },
            {
                'name': 'Information Systems',
                'code': 'IS',
                'degree_level': Program.DegreeLevel.BACHELOR,
                'department': 'Computer Science',
                'faculty': 'Science and Technology',
                'duration_years': 4.0,
                'is_active': True,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for program_data in programs_to_add:
            program_name = program_data['name']
            program_code = program_data['code']
            
            # Check if program already exists
            existing_program = Program.objects.filter(
                institution=institution,
                code=program_code
            ).first()
            
            if existing_program:
                # Update existing program
                for key, value in program_data.items():
                    if key != 'code':  # Don't update code
                        setattr(existing_program, key, value)
                existing_program.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated existing program: {program_name} ({program_code})'))
            else:
                # Create new program
                Program.objects.create(
                    institution=institution,
                    **program_data
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created program: {program_name} ({program_code})'))
        
        # Display summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Program Addition Summary:'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Institution: {institution.name}')
        self.stdout.write(f'Programs created: {created_count}')
        self.stdout.write(f'Programs updated: {updated_count}')
        self.stdout.write(self.style.SUCCESS('='*60))
        
        # List all programs for this institution
        all_programs = Program.objects.filter(institution=institution).order_by('name')
        if all_programs.exists():
            self.stdout.write(f'\nAll programs for {institution.name}:')
            for prog in all_programs:
                status = 'Active' if prog.is_active else 'Inactive'
                self.stdout.write(f'  - {prog.name} ({prog.code}) - {prog.get_degree_level_display()} - {status}')

