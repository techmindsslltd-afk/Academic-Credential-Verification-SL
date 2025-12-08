"""
Management command to create sample students for testing
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random
from apps.accounts.models import User, UserRole, StudentProfile
from apps.institutions.models import Institution


class Command(BaseCommand):
    help = 'Create sample students for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of sample students to create (default: 20)',
        )
        parser.add_argument(
            '--institution',
            type=str,
            help='Institution name or ID to assign students to',
        )

    def handle(self, *args, **options):
        count = options['count']
        institution_name = options.get('institution')
        
        # Get or create institution
        if institution_name:
            try:
                # Try exact match first
                institution = Institution.objects.filter(name__iexact=institution_name).first()
                if not institution:
                    # Try contains match and get first result
                    institution = Institution.objects.filter(name__icontains=institution_name).first()
                if not institution:
                    # Try by ID
                    try:
                        institution = Institution.objects.get(id=institution_name)
                    except:
                        pass
                if not institution:
                    self.stdout.write(self.style.ERROR(f'Institution "{institution_name}" not found'))
                    return
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error finding institution: {str(e)}'))
                return
        else:
            institution = Institution.objects.first()
            if not institution:
                self.stdout.write(self.style.ERROR('No institution found. Please create an institution first.'))
                return
        
        self.stdout.write(f'Creating {count} sample students for {institution.name}...')
        
        # Sample data
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'James', 'Jessica',
            'Robert', 'Amanda', 'William', 'Melissa', 'Richard', 'Michelle', 'Joseph', 'Kimberly',
            'Thomas', 'Ashley', 'Christopher', 'Amy', 'Daniel', 'Angela', 'Matthew', 'Brenda',
            'Anthony', 'Emma', 'Mark', 'Olivia', 'Donald', 'Cynthia', 'Steven', 'Marie',
            'Paul', 'Janet', 'Andrew', 'Catherine', 'Joshua', 'Frances', 'Kenneth', 'Christine',
            'Kevin', 'Samantha', 'Brian', 'Deborah', 'George', 'Rachel', 'Timothy', 'Carolyn',
            'Ronald', 'Janet', 'Jason', 'Lisa', 'Edward', 'Nancy', 'Jeffrey', 'Betty',
            'Ryan', 'Margaret', 'Jacob', 'Sandra', 'Gary', 'Ashley', 'Nicholas', 'Kimberly',
            'Eric', 'Donna', 'Jonathan', 'Emily', 'Stephen', 'Michelle', 'Larry', 'Carol',
            'Justin', 'Amanda', 'Scott', 'Dorothy', 'Brandon', 'Melissa', 'Benjamin', 'Debra',
            'Samuel', 'Stephanie', 'Frank', 'Rebecca', 'Gregory', 'Sharon', 'Raymond', 'Laura',
            'Alexander', 'Cynthia', 'Patrick', 'Kathleen', 'Jack', 'Amy', 'Dennis', 'Angela',
            'Jerry', 'Shirley', 'Tyler', 'Anna', 'Aaron', 'Brenda', 'Jose', 'Pamela',
            'Henry', 'Emma', 'Adam', 'Nicole', 'Douglas', 'Virginia', 'Nathan', 'Catherine',
            'Zachary', 'Christine', 'Kyle', 'Samantha', 'Noah', 'Deborah', 'Ethan', 'Rachel',
            'Jeremy', 'Carolyn', 'Walter', 'Janet', 'Christian', 'Catherine', 'Keith', 'Frances',
            'Roger', 'Marie', 'Terry', 'Christine', 'Gerald', 'Samantha', 'Harold', 'Deborah',
            'Sean', 'Rachel', 'Austin', 'Carolyn', 'Carl', 'Janet', 'Arthur', 'Catherine',
            'Lawrence', 'Frances', 'Dylan', 'Marie', 'Jesse', 'Christine', 'Jordan', 'Samantha',
            'Bryan', 'Deborah', 'Billy', 'Rachel', 'Bruce', 'Carolyn', 'Gabriel', 'Janet',
            'Logan', 'Catherine', 'Alan', 'Frances', 'Juan', 'Marie', 'Wayne', 'Christine',
            'Roy', 'Samantha', 'Ralph', 'Deborah', 'Randy', 'Rachel', 'Eugene', 'Carolyn',
            'Vincent', 'Janet', 'Russell', 'Catherine', 'Louis', 'Frances', 'Philip', 'Marie',
            'Bobby', 'Christine', 'Johnny', 'Samantha', 'Earl', 'Deborah', 'Jimmy', 'Rachel',
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
            'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Wilson', 'Anderson', 'Thomas', 'Taylor',
            'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White', 'Harris', 'Sanchez',
            'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King',
            'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green', 'Adams',
            'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts',
            'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker', 'Cruz', 'Edwards',
            'Collins', 'Reyes', 'Stewart', 'Morris', 'Morales', 'Murphy', 'Cook', 'Rogers',
            'Gutierrez', 'Ortiz', 'Morgan', 'Cooper', 'Peterson', 'Bailey', 'Reed', 'Kelly',
            'Howard', 'Ramos', 'Kim', 'Cox', 'Ward', 'Richardson', 'Watson', 'Brooks',
            'Chavez', 'Wood', 'James', 'Bennett', 'Gray', 'Mendoza', 'Ruiz', 'Hughes',
            'Price', 'Alvarez', 'Castillo', 'Sanders', 'Patel', 'Myers', 'Long', 'Ross',
            'Foster', 'Jimenez', 'Powell', 'Jenkins', 'Perry', 'Russell', 'Sullivan', 'Bell',
            'Coleman', 'Butler', 'Henderson', 'Barnes', 'Gonzales', 'Fisher', 'Vasquez', 'Simmons',
            'Romero', 'Jordan', 'Patterson', 'Alexander', 'Hamilton', 'Graham', 'Reynolds', 'Griffin',
            'Wallace', 'Moreno', 'West', 'Cole', 'Hayes', 'Bryant', 'Herrera', 'Gibson',
            'Ellis', 'Tran', 'Medina', 'Aguilar', 'Stevens', 'Murray', 'Ford', 'Castro',
            'Marshall', 'Owens', 'Harrison', 'Fernandez', 'Mcdonald', 'Woods', 'Washington', 'Kennedy',
            'Wells', 'Vargas', 'Henry', 'Chen', 'Freeman', 'Webb', 'Tucker', 'Guzman',
            'Burns', 'Crawford', 'Olson', 'Simpson', 'Porter', 'Hunter', 'Gordon', 'Mendez',
            'Silva', 'Shaw', 'Snyder', 'Mason', 'Dixon', 'Munoz', 'Hunt', 'Hicks',
            'Holmes', 'Palmer', 'Wagner', 'Black', 'Robertson', 'Boyd', 'Rose', 'Stone',
            'Salazar', 'Fox', 'Warren', 'Mills', 'Meyer', 'Rice', 'Schmidt', 'Garza',
            'Daniels', 'Ferguson', 'Nichols', 'Stephens', 'Soto', 'Weaver', 'Ryan', 'Gardner',
            'Payne', 'Grant', 'Dunn', 'Kelley', 'Spencer', 'Hawkins', 'Arnold', 'Pierce',
            'Vazquez', 'Hansen', 'Peters', 'Santos', 'Hart', 'Bradley', 'Knight', 'Elliott',
            'Cunningham', 'Duncan', 'Armstrong', 'Hudson', 'Carroll', 'Lane', 'Riley', 'Andrews',
            'Alvarado', 'Ray', 'Delgado', 'Berry', 'Perkins', 'Hoffman', 'Johnston', 'Matthews',
            'Pena', 'Richards', 'Contreras', 'Willis', 'Carpenter', 'Lawrence', 'Sandoval', 'Guerrero',
            'George', 'Chapman', 'Rios', 'Estrada', 'Ortega', 'Watkins', 'Greene', 'Nunez',
            'Wheeler', 'Valdez', 'Harper', 'Lynch', 'Barker', 'Maldonado', 'Day', 'Vaughn',
            'Mejia', 'Walters', 'Burton', 'Acevedo', 'Montoya', 'Tate', 'Mcneil', 'Hahn',
            'Hinton', 'Barrera', 'Mccall', 'Mckinney', 'Barr', 'Mccarthy', 'Mccormick', 'Mccoy',
            'Mcdowell', 'Mcfarland', 'Mckee', 'Mcknight', 'Mclaughlin', 'Mclean', 'Mcmillan', 'Mcpherson',
        ]
        
        programs = [
            'Bachelor of Science in Computer Science',
            'Bachelor of Science in Information Technology',
            'Bachelor of Arts in Economics',
            'Bachelor of Science in Mathematics',
            'Bachelor of Science in Physics',
            'Bachelor of Science in Chemistry',
            'Bachelor of Science in Biology',
            'Bachelor of Arts in English',
            'Bachelor of Arts in History',
            'Bachelor of Science in Engineering',
            'Master of Business Administration',
            'Master of Science in Computer Science',
            'Bachelor of Science in Nursing',
            'Bachelor of Science in Accounting',
            'Bachelor of Arts in Psychology',
            'Bachelor of Science in Environmental Science',
            'Bachelor of Arts in Sociology',
            'Bachelor of Science in Statistics',
            'Bachelor of Arts in Political Science',
            'Bachelor of Science in Biochemistry',
        ]
        
        nationalities = [
            'Sierra Leonean', 'Nigerian', 'Ghanaian', 'Kenyan', 'South African',
            'American', 'British', 'Canadian', 'Australian', 'Indian',
            'Chinese', 'Japanese', 'Brazilian', 'Mexican', 'French',
            'German', 'Italian', 'Spanish', 'Dutch', 'Swedish',
        ]
        
        created_count = 0
        skipped_count = 0
        
        for i in range(count):
            try:
                # Generate random data
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                email = f"{first_name.lower()}.{last_name.lower()}{i+1}@student.{institution.short_name.lower() if institution.short_name else 'edu'}.sl"
                
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    skipped_count += 1
                    continue
                
                # Generate student ID
                year = timezone.now().year
                student_id = f"STU{year}{random.randint(1000, 9999)}"
                
                # Create user
                user = User.objects.create_user(
                    email=email,
                    password='Student@123',
                    first_name=first_name,
                    last_name=last_name,
                    phone=f"+232{random.randint(70000000, 79999999)}",
                    role=UserRole.STUDENT,
                    is_active=True,
                    is_verified=random.choice([True, False]),
                )
                
                # Create or update student profile
                enrollment_date = date.today() - timedelta(days=random.randint(30, 1000))
                graduation_date = None
                if random.choice([True, False]):
                    graduation_date = enrollment_date + timedelta(days=random.randint(1095, 1460))  # 3-4 years
                
                # Check if profile already exists
                try:
                    student_profile = StudentProfile.objects.get(user=user)
                    # Profile exists, update it
                    student_profile.institution = institution
                    if not student_profile.student_id:
                        student_profile.student_id = student_id
                    if not student_profile.program:
                        student_profile.program = random.choice(programs)
                    if not student_profile.enrollment_date:
                        student_profile.enrollment_date = enrollment_date
                    student_profile.save()
                except StudentProfile.DoesNotExist:
                    # Create new profile
                    StudentProfile.objects.create(
                        user=user,
                        institution=institution,
                        student_id=student_id,
                        date_of_birth=date(1995, 1, 1) + timedelta(days=random.randint(0, 7300)),  # Age 18-38
                        nationality=random.choice(nationalities),
                        address=f"{random.randint(1, 999)} Main Street, Freetown, Sierra Leone",
                        program=random.choice(programs),
                        enrollment_date=enrollment_date,
                        graduation_date=graduation_date,
                    )
                
                created_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating student {i+1}: {str(e)}'))
                skipped_count += 1
                continue
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {created_count} sample students for {institution.name}'
        ))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'Skipped {skipped_count} students (duplicates or errors)'))

