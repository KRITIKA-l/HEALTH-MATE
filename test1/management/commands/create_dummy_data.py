from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from test1.models import UserProfile, District, Disease, Report
import random


class Command(BaseCommand):
    help = 'Create dummy users, districts, diseases and reports'

    def add_arguments(self, parser):
        parser.add_argument('--reports', type=int, default=100, help='Number of reports to create')
        parser.add_argument('--users', type=int, default=10, help='Number of additional random users to create')

    def handle(self, *args, **options):
        created = 0

        # 1) Create the specific users you requested
        # Super/admin user
        if not User.objects.filter(username='KRITIKA').exists():
            u = User.objects.create_user(username='KRITIKA', password='kam2346', email='kritika@example.com')
            u.is_staff = True
            u.is_superuser = True
            u.save()
            UserProfile.objects.create(user=u, role='admin')
            self.stdout.write(self.style.SUCCESS('Created user: KRITIKA (admin)'))
            created += 1
        else:
            self.stdout.write('User KRITIKA already exists, skipping')

        # Create three manav variants (one for each role). Use unique usernames.
        manav_variants = [
            ('manav_env', 'manavrachna', 'environment_officer'),
            ('manav_vet', 'manavrachna', 'veterinary_officer'),
            ('manav_human', 'manavrachna', 'health_worker'),
        ]

        for uname, pwd, role in manav_variants:
            if not User.objects.filter(username=uname).exists():
                u = User.objects.create_user(username=uname, password=pwd, email=f'{uname}@example.com')
                UserProfile.objects.create(user=u, role=role)
                self.stdout.write(self.style.SUCCESS(f'Created user: {uname} ({role})'))
                created += 1
            else:
                self.stdout.write(f'User {uname} already exists, skipping')

        # 2) Additional random users (useful as reporters)
        extra = options.get('users', 10) or 10
        roles = [r[0] for r in UserProfile.ROLE_CHOICES]
        for i in range(extra):
            uname = f'dummyuser{i+1}'
            if User.objects.filter(username=uname).exists():
                continue
            u = User.objects.create_user(username=uname, password='password123', email=f'{uname}@example.com')
            role = random.choice(roles)
            UserProfile.objects.create(user=u, role=role)
            created += 1

        # 3) Create sample districts
        sample_district_names = [
            'Aldea','Brookfield','Cedar Grove','Dunhill','Eversham','Foxford','Greenvale','Hillcrest',
            'Ironwood','Jasper','Kingsley','Lakeside','Meadowbrook','Northfield','Oakridge','Pineview',
            'Quarrytown','Riverview','Springfield','Westhaven'
        ]

        districts = []
        for name in sample_district_names:
            d, _ = District.objects.get_or_create(name=f'District {name}', defaults={'state': 'State X', 'population': random.randint(20000, 500000)})
            districts.append(d)

        # 4) Create sample diseases
        sample_diseases = [
            ('Influenza', 'human'), ('Malaria', 'human'), ('COVID-19', 'human'), ('Rabies', 'animal'),
            ('Foot-and-mouth', 'animal'), ('Cholera', 'human'), ('Dengue', 'human'), ('Avian influenza', 'animal'),
            ('Leptospirosis', 'human'), ('E.coli contamination', 'environmental'), ('Salmonella', 'human'),
            ('Brucellosis', 'animal'), ('Zika', 'human'), ('Lyme disease', 'human'), ('Anthrax', 'animal'),
            ('Tuberculosis', 'human'), ('Norovirus', 'human'), ('Chikungunya', 'human'), ('Hendra', 'animal'), ('Toxoplasmosis', 'animal')
        ]

        diseases = []
        for name, cat in sample_diseases:
            dis, _ = Disease.objects.get_or_create(name=name, defaults={'category': cat, 'symptoms': 'Sample symptoms', 'severity': 'Moderate'})
            diseases.append(dis)

        # 5) Create reports (at least the requested number)
        num_reports = options.get('reports', 100) or 100
        profiles = list(UserProfile.objects.all())
        if not profiles:
            self.stdout.write(self.style.WARNING('No UserProfiles found — reports will be created with null reporter.'))

        for i in range(num_reports):
            district = random.choice(districts)
            disease = random.choice(diseases)
            reporter = random.choice(profiles) if profiles else None
            Report.objects.create(
                district=district,
                disease=disease,
                number_of_cases=random.randint(1, 500),
                deaths=random.randint(0, 50),
                source='dummy import',
                reporter=reporter
            )

        self.stdout.write(self.style.SUCCESS(f'Created {created} users (or skipped existing) and {num_reports} reports.'))
