from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Q
from test1.models import UserProfile, District, Disease, Report


class Command(BaseCommand):
    help = 'Delete dummy data created by create_dummy_data command'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true', help='Skip confirmation prompt')

    def handle(self, *args, **options):
        confirm = options.get('yes', False)

        # Targets (should match what create_dummy_data created)
        user_exact = ['KRITIKA', 'manav_env', 'manav_vet', 'manav_human']
        user_prefix = 'dummyuser'
        district_prefix = 'District '
        sample_diseases = [
            'Influenza','Malaria','COVID-19','Rabies','Foot-and-mouth','Cholera','Dengue','Avian influenza',
            'Leptospirosis','E.coli contamination','Salmonella','Brucellosis','Zika','Lyme disease','Anthrax',
            'Tuberculosis','Norovirus','Chikungunya','Hendra','Toxoplasmosis'
        ]

        # Querysets to delete
        users_qs = User.objects.filter(Q(username__in=user_exact) | Q(username__startswith=user_prefix))
        districts_qs = District.objects.filter(name__startswith=district_prefix)
        diseases_qs = Disease.objects.filter(name__in=sample_diseases)
        reports_qs = Report.objects.filter(source='dummy import')

        summary = {
            'users': users_qs.count(),
            'districts': districts_qs.count(),
            'diseases': diseases_qs.count(),
            'reports': reports_qs.count(),
        }

        self.stdout.write('About to delete the following dummy data:')
        self.stdout.write(f"  Users matching {user_exact} or starting with '{user_prefix}': {summary['users']}")
        self.stdout.write(f"  Districts starting with '{district_prefix}': {summary['districts']}")
        self.stdout.write(f"  Diseases in sample list: {summary['diseases']}")
        self.stdout.write(f"  Reports with source='dummy import': {summary['reports']}")

        if not confirm:
            ans = input('Proceed with deletion? Type YES to confirm: ')
            if ans.strip() != 'YES':
                self.stdout.write(self.style.NOTICE('Aborted — no changes made.'))
                return

        # Perform deletions
        reports_deleted = reports_qs.delete()
        diseases_deleted = diseases_qs.delete()
        districts_deleted = districts_qs.delete()
        users_deleted = users_qs.delete()

        self.stdout.write(self.style.SUCCESS(f"Deleted reports: {reports_deleted[0]}"))
        self.stdout.write(self.style.SUCCESS(f"Deleted diseases: {diseases_deleted[0]}"))
        self.stdout.write(self.style.SUCCESS(f"Deleted districts: {districts_deleted[0]}"))
        self.stdout.write(self.style.SUCCESS(f"Deleted users: {users_deleted[0]}"))
