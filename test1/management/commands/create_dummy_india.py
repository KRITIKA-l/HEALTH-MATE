from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
import random

from test1.models import UserProfile, District, Disease, Report, VoiceReport


class Command(BaseCommand):
    help = 'Create dummy India-focused data using only the four provided user credentials'

    def add_arguments(self, parser):
        parser.add_argument('--reports', type=int, default=200, help='Number of reports to create')
        parser.add_argument('--districts', type=int, default=50, help='Number of districts to ensure')
        parser.add_argument('--diseases', type=int, default=20, help='Number of diseases to ensure')
        parser.add_argument('--voices', type=int, default=10, help='Number of voice reports to create')

    def handle(self, *args, **options):
        # Four provided credentials only
        users_spec = [
            ('KRITIKA', 'kam2346', 'kritika@example.com', 'admin'),
            ('manav_env', 'manavrachna', 'manav_env@example.com', 'environment_officer'),
            ('manav_vet', 'manavrachna', 'manav_vet@example.com', 'veterinary_officer'),
            ('manav_human', 'manavrachna', 'manav_human@example.com', 'health_worker'),
        ]

        created_users = 0
        profiles = []

        self.stdout.write(self.style.NOTICE("\n🔹 Ensuring users and profiles...\n"))

        for username, pwd, email, role in users_spec:
            user, created = User.objects.get_or_create(username=username, defaults={'email': email})
            if created:
                user.set_password(pwd)
                if username == 'KRITIKA':
                    user.is_staff = True
                    user.is_superuser = True
                user.save()
                created_users += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Created user: {username} ({role})'))
            else:
                self.stdout.write(f'ℹ️ User {username} already exists')

            # Ensure UserProfile exists and has correct role
            profile, pcreated = UserProfile.objects.get_or_create(user=user, defaults={'role': role})
            if not pcreated and profile.role != role:
                profile.role = role
                profile.save()
            profiles.append(profile)

        # Districts
        self.stdout.write(self.style.NOTICE("\n🏙️ Creating Indian districts...\n"))
        indian_districts = [
            'Mumbai','Delhi','Bengaluru','Chennai','Kolkata','Pune','Hyderabad','Ahmedabad','Surat','Jaipur',
            'Lucknow','Kanpur','Nagpur','Indore','Bhopal','Thane','Visakhapatnam','Patna','Ludhiana','Agra',
            'Varanasi','Coimbatore','Madurai','Mysuru','Mangalore','Bhubaneswar','Cuttack','Guwahati','Chandigarh','Raipur',
            'Dehradun','Shimla','Srinagar','Jammu','Jodhpur','Udaipur','Agartala','Imphal','Shillong','Panaji',
            'Thiruvananthapuram','Kochi','Rajkot','Vadodara','Nashik','Amritsar','Jalandhar','Bareilly','Meerut','Aligarh'
        ]

        districts_needed = options['districts']
        districts = []
        for name in indian_districts[:districts_needed]:
            d, _ = District.objects.get_or_create(
                name=f'District {name}',
                defaults={'state': 'India', 'population': random.randint(50000, 5000000)}
            )
            districts.append(d)

        # Diseases
        self.stdout.write(self.style.NOTICE("\n🦠 Creating diseases...\n"))
        indian_diseases = [
            ('Dengue', 'human'), ('Malaria', 'human'), ('Tuberculosis', 'human'), ('Cholera', 'human'),
            ('Typhoid', 'human'), ('Hepatitis A', 'human'), ('Hepatitis B', 'human'), ('Leptospirosis', 'human'),
            ('COVID-19', 'human'), ('Influenza', 'human'), ('Rabies', 'animal'), ('Scrub typhus', 'human'),
            ('Kala-azar', 'human'), ('Japanese encephalitis', 'human'), ('Anthrax', 'animal'), ('Brucellosis', 'animal'),
            ('Zika', 'human'), ('Leishmaniasis', 'human'), ('Chikungunya', 'human'), ('Norovirus', 'human')
        ]

        diseases_needed = options['diseases']
        diseases = []
        for name, cat in indian_diseases[:diseases_needed]:
            dis, _ = Disease.objects.get_or_create(
                name=name,
                defaults={'category': cat, 'symptoms': 'Common symptoms', 'severity': 'Variable'}
            )
            diseases.append(dis)

        # Reports
        self.stdout.write(self.style.NOTICE("\n📊 Creating random reports...\n"))
        num_reports = options['reports']
        for i in range(num_reports):
            district = random.choice(districts)
            disease = random.choice(diseases)
            reporter = random.choice(profiles)
            Report.objects.create(
                district=district,
                disease=disease,
                number_of_cases=random.randint(1, 1000),
                deaths=random.randint(0, 50),
                source='dummy_india_import',
                reporter=reporter
            )

        # Voice Reports
        self.stdout.write(self.style.NOTICE("\n🎤 Creating dummy voice reports...\n"))
        num_voices = options['voices']
        for i in range(num_voices):
            reporter = random.choice(profiles)
            vr = VoiceReport(reporter=reporter, transcribed_text='Dummy transcription', status='pending')
            filename = f'voice_reports/{reporter.user.username}_voice_{i+1}.txt'
            content = ContentFile(b'Dummy voice content')
            vr.audio_file.save(filename, content, save=False)
            vr.save()

        self.stdout.write(self.style.SUCCESS("\n✅ Dummy data creation completed successfully!\n"))
        self.stdout.write(self.style.SUCCESS(f"Users ensured: {len(profiles)}"))
        self.stdout.write(self.style.SUCCESS(f"Districts: {len(districts)}, Diseases: {len(diseases)}"))
        self.stdout.write(self.style.SUCCESS(f"Reports created: {num_reports}, Voice reports: {num_voices}\n"))
