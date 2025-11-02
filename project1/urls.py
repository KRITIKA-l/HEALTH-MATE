"""
URL configuration for project1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from test1 import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Home page
    path('', views.home, name='home'),

    path('about/', views.about_view, name='about'),
    path('public-statistics/', views.public_statistics, name='public_statistics'),
    path('profile/', views.profile_view, name='profile_view'),

    # Django built-in admin panel
    path('admin/', admin.site.urls),

    # Authentication
    path('login/', views.login_user, name='loginuser'),
    path('signup/', views.signup_user, name='signupuser'),
    path('logout/', views.logout_user, name='logoutuser'),

    # Dashboards
    path('animal-dashboard/', views.animal_dashboard, name='animal_dashboard'),
    path('add-animal-report/', views.add_animal_report, name='add_animal_report'),
    path('my-animal-reports/', views.my_animal_reports, name='my_animal_reports'),
    path('district-data/', views.district_data, name='district_data'),

    path('human-dashboard/', views.human_dashboard, name='human_dashboard'),
    path('add-report/', views.add_report, name='add_report'),
    path('voice-report/', views.voice_report, name='voice_report'),
    path('my-reports/', views.my_reports, name='my_reports'),
    path("my-reports/", views.my_reports, name="my_reports"),
    path("download-my-reports/", views.download_my_reports, name="download_my_reports"),

    path('environment-dashboard/', views.environment_dashboard, name='environment_dashboard'),
    path('environment-reports/', views.environment_reports, name='environment_reports'),
    path('add-environment-report/', views.add_environment_report, name='add_environment_report'),
    path('environment-overview/', views.environment_overview, name='environment_overview'),

    # Admin sections (your normal URLs)
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-reports/', views.manage_reports, name='manage_reports'),
    path('districts/', views.districts_view, name='districts_view'),
    path('diseases/', views.diseases_view, name='diseases_view'),
    path('download-all-reports/', views.download_all_reports, name='download_all_reports'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

