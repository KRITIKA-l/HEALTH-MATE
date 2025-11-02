from django.contrib import admin
from .models import UserProfile, District, Disease, Report, VoiceReport


# -------------------------
# USER PROFILE ADMIN
# -------------------------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'district')
    list_filter = ('role', 'district')
    search_fields = ('user__username', 'phone', 'district')
    ordering = ('role', 'user__username')


# -------------------------
# DISTRICT ADMIN
# -------------------------
@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'population')
    list_filter = ('state',)
    search_fields = ('name', 'state')
    ordering = ('state', 'name')


# -------------------------
# DISEASE ADMIN
# -------------------------
@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'severity')
    list_filter = ('category', 'severity')
    search_fields = ('name', 'symptoms')
    ordering = ('category', 'name')


# -------------------------
# REPORT ADMIN
# -------------------------
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'disease', 'district', 'number_of_cases',
        'deaths', 'source', 'date_reported', 'reporter'
    )
    list_filter = ('disease__category', 'district__state', 'date_reported')
    search_fields = ('disease__name', 'district__name', 'reporter__user__username', 'source')
    date_hierarchy = 'date_reported'
    ordering = ('-date_reported',)


# -------------------------
# VOICE REPORT ADMIN
# -------------------------
@admin.register(VoiceReport)
class VoiceReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('reporter__user__username', 'transcribed_text')
    ordering = ('-timestamp',)
