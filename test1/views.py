from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from .models import Report, District, Disease, VoiceReport
from django.db.models import Count
from django.shortcuts import redirect
import json
from django.db.models import Sum
from django.contrib import messages
from django.utils import timezone
import csv
from django.http import HttpResponse


def home(request):
    return render(request, 'test1/home.html')


def about_view(request):
    return render(request, 'test1/about.html')

def public_statistics(request):
    # Aggregate data by category
    human_cases = Report.objects.filter(disease__category='human').aggregate(Sum('number_of_cases'))['number_of_cases__sum'] or 0
    animal_cases = Report.objects.filter(disease__category='animal').aggregate(Sum('number_of_cases'))['number_of_cases__sum'] or 0
    env_cases = Report.objects.filter(disease__category='environmental').aggregate(Sum('number_of_cases'))['number_of_cases__sum'] or 0

    total_cases = human_cases + animal_cases + env_cases

    # Category percentages
    if total_cases:
        human_percent = round((human_cases / total_cases) * 100, 1)
        animal_percent = round((animal_cases / total_cases) * 100, 1)
        env_percent = round((env_cases / total_cases) * 100, 1)
    else:
        human_percent = animal_percent = env_percent = 0

    # Top category
    category_data = {
        "Human": human_percent,
        "Animal": animal_percent,
        "Environmental": env_percent
    }
    top_category = max(category_data, key=category_data.get) if total_cases else None
    top_percent = category_data[top_category] if top_category else 0

    # Top 3 Districts
    top_districts = (
        Report.objects.values('district__name')
        .annotate(total_cases=Sum('number_of_cases'))
        .order_by('-total_cases')[:3]
    )

    # Top 3 Diseases
    top_diseases = (
        Report.objects.values('disease__name')
        .annotate(total_cases=Sum('number_of_cases'))
        .order_by('-total_cases')[:3]
    )

    context = {
        'total_human_cases': human_cases,
        'total_animal_cases': animal_cases,
        'total_environmental_cases': env_cases,
        'total_cases': total_cases,
        'human_percent': human_percent,
        'animal_percent': animal_percent,
        'environmental_percent': env_percent,
        'top_category': top_category,
        'top_percent': top_percent,
        'top_districts': top_districts,
        'top_diseases': top_diseases,
    }
    return render(request, 'test1/statistics.html', context)

@login_required
def profile_view(request):
    """Display and optionally edit the user's profile."""
    user_profile = request.user.userprofile

    if request.method == "POST":
        phone = request.POST.get("phone")
        district = request.POST.get("district")

        # Allow editing only phone and district
        user_profile.phone = phone
        user_profile.district = district
        user_profile.save()

        messages.success(request, "✅ Profile updated successfully!")
        return redirect("profile_view")

    return render(request, "test1/profile.html", {"user_profile": user_profile})


# 🔐 Login user
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            role = user.userprofile.role

            if role == "admin":
                return redirect('admin_dashboard')
            elif role == "health_worker":
                return redirect('human_dashboard')
            elif role == "veterinary_officer":
                return redirect('animal_dashboard')
            elif role == "environment_officer":
                return redirect('environment_dashboard')
            else:
                return redirect('home')

        return render(request, 'test1/login.html', {'error': 'Invalid username or password'})

    # Already logged in? go to correct dashboard
    if request.user.is_authenticated:
        role = request.user.userprofile.role
        if role == "admin":
            return redirect('admin_dashboard')
        elif role == "health_worker":
            return redirect('human_dashboard')
        elif role == "veterinary_officer":
            return redirect('animal_dashboard')
        elif role == "environment_officer":
            return redirect('env_dashboard')
    return render(request, 'test1/login.html')


# 🧾 Signup user
def signup_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')

        if password1 != password2:
            return render(request, 'test1/signup.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'test1/signup.html', {'error': 'Username already taken'})

        user = User.objects.create_user(username=username, email=email, password=password1)
        UserProfile.objects.create(user=user, role=role)
        login(request, user)

        if role == "admin":
            return redirect('admin_dashboard')
        elif role == "health_worker":
            return redirect('human_dashboard')
        elif role == "veterinary_officer":
            return redirect('animal_dashboard')
        elif role == "environment_officer":
            return redirect('env_dashboard')
        else:
            return redirect('home')

    return render(request, 'test1/signup.html')

# 🚪 Logout user
def logout_user(request):
    logout(request)
    return redirect('home')

@login_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_reports = Report.objects.count()
    total_districts = District.objects.count()
    total_diseases = Disease.objects.count()

    district_data = list(Report.objects.values_list('district__name').annotate(Count('id')))
    disease_data = list(Report.objects.values_list('disease__name').annotate(Count('id')))
    user_data = list(Report.objects.values_list('reporter__user__username').annotate(Count('id')))

    context = {
        'total_users': total_users,
        'total_reports': total_reports,
        'total_districts': total_districts,
        'total_diseases': total_diseases,
        'district_data_json': json.dumps([["District", "Reports"]] + district_data),
        'disease_data_json': json.dumps([["Disease", "Reports"]] + disease_data),
        'user_data_json': json.dumps([["User", "Reports"]] + user_data),
    }
    return render(request, 'test1/admin_dashboard.html', context)

# 🧑‍💼 Manage Users Page
@login_required
def manage_users(request):
    users = UserProfile.objects.select_related('user').all()
    return render(request, 'test1/manage_users.html', {'users': users})


# 📋 Reports Overview Page
@login_required
def manage_reports(request):
    reports = Report.objects.select_related('disease', 'district', 'reporter__user')

    total_reports = reports.count()
    human_reports = reports.filter(disease__category='human').count()
    animal_reports = reports.filter(disease__category='animal').count()
    environmental_reports = reports.filter(disease__category='environmental').count()

    context = {
        'reports': reports,
        'total_reports': total_reports,
        'human_reports': human_reports,
        'animal_reports': animal_reports,
        'environmental_reports': environmental_reports,
    }
    return render(request, 'test1/manage_reports.html', context)

def districts_view(request):
    # Annotate each district with number of related reports
    districts = District.objects.annotate(report_count=Count('report'))

    total_districts = districts.count()
    total_reports = Report.objects.count()
    most_affected = districts.order_by('-report_count').first()

    chart_data = [
        {'name': d.name, 'report_count': d.report_count} for d in districts
    ]

    return render(request, 'test1/districts.html', {
        'districts': districts,
        'total_districts': total_districts,
        'total_reports': total_reports,
        'most_affected_district': most_affected.name if most_affected else "N/A",
        'chart_data': chart_data
    })

def diseases_view(request):
    # Annotate each disease with total reports
    diseases = Disease.objects.annotate(report_count=Count('report'))

    total_diseases = diseases.count()
    total_reports = Report.objects.count()
    critical_diseases = diseases.filter(severity__icontains="High").count()

    # Calculate total cases and recent reports
    total_cases = Report.objects.aggregate(total_cases=Sum('number_of_cases'))['total_cases'] or 0
    recent_reports = Report.objects.filter(date_reported__year=2025).count()

    # Prepare chart data
    chart_data = [
        {'name': d.name, 'report_count': d.report_count or 0}
        for d in diseases
    ]

    context = {
        'diseases': diseases,
        'total_diseases': total_diseases,
        'total_cases': total_cases,
        'critical_diseases': critical_diseases,
        'recent_reports': recent_reports,
        'chart_data': chart_data,
    }
    return render(request, 'test1/diseases.html', context)

@login_required
def human_dashboard(request):
    """Dashboard showing data submitted by the logged-in health officer."""

    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Filter reports submitted by this user only
    reports = Report.objects.filter(reporter=user_profile, disease__category='human')

    # Compute stats for this specific officer
    total_reports = reports.count()
    total_cases = reports.aggregate(Sum('number_of_cases'))['number_of_cases__sum'] or 0
    total_deaths = reports.aggregate(Sum('deaths'))['deaths__sum'] or 0

    # Get top disease (by total cases)
    top_disease_data = (
        reports.values('disease__name')
        .annotate(total_cases=Sum('number_of_cases'))
        .order_by('-total_cases')
        .first()
    )
    top_disease = top_disease_data['disease__name'] if top_disease_data else "N/A"

    # Get most recent report date
    last_report = reports.order_by('-date_reported').first()
    last_date = last_report.date_reported if last_report else "No reports yet"

    context = {
        'total_reports': total_reports,
        'total_cases': total_cases,
        'total_deaths': total_deaths,
        'top_disease': top_disease,
        'last_date': last_date,
    }

    return render(request, 'test1/human_dashboard.html', context)

@login_required
def add_report(request):
    """Allows a health officer to manually add a new report."""

    user_profile = get_object_or_404(UserProfile, user=request.user)
    diseases = Disease.objects.filter(category='human')
    districts = District.objects.all()

    if request.method == 'POST':
        district_id = request.POST.get('district')
        disease_id = request.POST.get('disease')
        number_of_cases = request.POST.get('number_of_cases')
        deaths = request.POST.get('deaths')
        source = request.POST.get('source')

        if not all([district_id, disease_id, number_of_cases]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('add_report')

        district = get_object_or_404(District, id=district_id)
        disease = get_object_or_404(Disease, id=disease_id)

        Report.objects.create(
            district=district,
            disease=disease,
            number_of_cases=number_of_cases,
            deaths=deaths or 0,
            source=source or "Manual Entry",
            reporter=user_profile
        )

        messages.success(request, "✅ Report added successfully!")
        return redirect('human_dashboard')

    context = {
        'diseases': diseases,
        'districts': districts,
    }
    return render(request, 'test1/add_report.html', context)


@login_required
def voice_report(request):
    """Handles uploading and managing voice-based reports."""

    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST' and request.FILES.get('audio_file'):
        audio = request.FILES['audio_file']

        VoiceReport.objects.create(
            reporter=user_profile,
            audio_file=audio,
            status='pending'
        )

        messages.success(request, "🎙️ Voice report uploaded successfully! Awaiting transcription.")
        return redirect('voice_report')

    voice_reports = VoiceReport.objects.filter(reporter=user_profile).order_by('-timestamp')
    return render(request, 'test1/voice_report.html', {'voice_reports': voice_reports})


@login_required
def my_reports(request):
    """Displays all reports submitted by the logged-in officer."""

    user_profile = get_object_or_404(UserProfile, user=request.user)
    reports = Report.objects.filter(reporter=user_profile).order_by('-date_reported')

    return render(request, 'test1/my_reports.html', {'reports': reports})

def my_reports(request):
    user_profile = UserProfile.objects.get(user=request.user)
    reports = Report.objects.filter(reporter=user_profile).order_by('-date_reported')

    total_cases = sum(r.number_of_cases for r in reports)
    total_deaths = sum(r.deaths for r in reports)

    return render(request, "test1/my_reports.html", {
        "reports": reports,
        "total_cases": total_cases,
        "total_deaths": total_deaths,
    })


def download_my_reports(request):
    user_profile = UserProfile.objects.get(user=request.user)
    reports = Report.objects.filter(reporter=user_profile)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_reports.csv"'

    writer = csv.writer(response)
    writer.writerow(['Disease', 'District', 'Cases', 'Deaths', 'Date Reported'])

    for r in reports:
        writer.writerow([
            r.disease.name,
            r.district.name,
            r.number_of_cases,
            r.deaths,
            r.date_reported.strftime("%d-%m-%Y"),
        ])

    return response

@login_required
def animal_dashboard(request):
    # Filter reports for animal category
    animal_reports = Report.objects.filter(disease__category='animal')

    total_cases = animal_reports.aggregate(Sum('number_of_cases'))['number_of_cases__sum'] or 0
    total_deaths = animal_reports.aggregate(Sum('deaths'))['deaths__sum'] or 0
    reports_added = animal_reports.count()
    districts_covered = animal_reports.values('district').distinct().count()

    context = {
        'animal_reports': animal_reports.order_by('-date_reported')[:10],
        'total_cases': total_cases,
        'total_deaths': total_deaths,
        'reports_added': reports_added,
        'districts_covered': districts_covered,
    }
    return render(request, 'test1/animal_dashboard.html', context)


@login_required
def add_animal_report(request):
    user_profile = UserProfile.objects.get(user=request.user)

    districts = District.objects.all()
    diseases = Disease.objects.filter(category='animal')

    if request.method == 'POST':
        district_id = request.POST.get('district')
        disease_id = request.POST.get('disease')
        number_of_cases = request.POST.get('number_of_cases')
        deaths = request.POST.get('deaths') or 0
        source = request.POST.get('source', '')

        district = District.objects.get(id=district_id)
        disease = Disease.objects.get(id=disease_id)

        Report.objects.create(
            district=district,
            disease=disease,
            number_of_cases=number_of_cases,
            deaths=deaths,
            source=source,
            reporter=user_profile
        )
        return redirect('my_animal_reports')

    context = {
        'districts': districts,
        'diseases': diseases,
    }
    return render(request, 'test1/add_animal_report.html', context)


@login_required
def my_animal_reports(request):
    user_profile = UserProfile.objects.get(user=request.user)
    reports = Report.objects.filter(reporter=user_profile, disease__category='animal')
    return render(request, 'test1/my_animal_reports.html', {'reports': reports})


@login_required
def district_data(request):
    districts = District.objects.all()

    # Add computed totals
    district_stats = []
    for d in districts:
        reports = Report.objects.filter(district=d, disease__category='animal')
        total_cases = reports.aggregate(Sum('number_of_cases'))['number_of_cases__sum'] or 0
        total_deaths = reports.aggregate(Sum('deaths'))['deaths__sum'] or 0

        district_stats.append({
            'name': d.name,
            'state': d.state,
            'population': d.population,
            'total_cases': total_cases,
            'total_deaths': total_deaths
        })

    return render(request, 'test1/district_data.html', {'districts': district_stats})

@login_required
def environment_dashboard(request):
    user_profile = request.user.userprofile

    # Fetch environmental reports only
    reports = Report.objects.filter(disease__category='environmental')

    total_reports = reports.count()
    active_districts = reports.values('district').distinct().count()
    pollution_cases = reports.aggregate(Sum('number_of_cases'))['number_of_cases__sum'] or 0
    critical_alerts = reports.filter(disease__severity__icontains='high').count()

    return render(request, 'test1/environment_dashboard.html', {
        'total_reports': total_reports,
        'active_districts': active_districts,
        'pollution_cases': pollution_cases,
        'critical_alerts': critical_alerts
    })


@login_required
def environment_reports(request):
    user_profile = request.user.userprofile
    reports = Report.objects.filter(
        reporter=user_profile,
        disease__category='environmental'
    ).select_related('district', 'disease').order_by('-date_reported')

    return render(request, 'test1/environment_reports.html', {'reports': reports})


@login_required
def add_environment_report(request):
    if request.method == 'POST':
        district_id = request.POST.get('district')
        disease_id = request.POST.get('disease')
        cases = request.POST.get('number_of_cases')
        deaths = request.POST.get('deaths') or 0
        source = request.POST.get('source', '')

        district = District.objects.get(id=district_id)
        disease = Disease.objects.get(id=disease_id)
        user_profile = request.user.userprofile

        Report.objects.create(
            district=district,
            disease=disease,
            number_of_cases=cases,
            deaths=deaths,
            source=source,
            reporter=user_profile
        )
        return redirect('environment_reports')

    districts = District.objects.all()
    diseases = Disease.objects.filter(category='environmental')
    return render(request, 'test1/add_environment_report.html', {
        'districts': districts,
        'diseases': diseases
    })


@login_required
def environment_overview(request):
    districts = District.objects.all()
    overview = []

    for d in districts:
        reports = Report.objects.filter(district=d, disease__category='environmental')
        total_cases = reports.aggregate(Sum('number_of_cases'))['number_of_cases__sum'] or 0
        avg_severity = "High" if total_cases > 50 else "Moderate" if total_cases > 20 else "Low"

        overview.append({
            'district': d.name,
            'state': d.state,
            'aqi': total_cases + 50,  # demo metric
            'water_quality': "Good" if total_cases < 20 else "Poor",
            'noise_level': f"{40 + total_cases//5} dB",
            'status': avg_severity
        })

    return render(request, 'test1/environment_overview.html', {'overview': overview})


@login_required
def download_all_reports(request):
    """Download all reports in CSV format (admin only)."""
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=401)

    # Create the HttpResponse object with CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_reports.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Disease Name', 'Category', 'District', 'State',
        'Date Reported', 'Cases', 'Deaths', 'Source', 'Reporter'
    ])

    reports = Report.objects.select_related('disease', 'district', 'reporter__user').all()

    for report in reports:
        writer.writerow([
            report.id,
            report.disease.name,
            report.disease.category,
            report.district.name,
            report.district.state,
            report.date_reported,
            report.number_of_cases,
            report.deaths,
            report.source,
            report.reporter.user.username if report.reporter else "N/A"
        ])

    return response