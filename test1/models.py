from django.db import models
from django.contrib.auth.models import User

# -------------------------
# USER & ROLE MANAGEMENT
# -------------------------
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('health_worker', 'Health Worker'),
        ('veterinary_officer', 'Veterinary Officer'),
        ('environment_officer', 'Environment Officer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    district = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# -------------------------
# DISTRICT & DISEASE DETAILS
# -------------------------
class District(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    population = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class Disease(models.Model):
    CATEGORY_CHOICES = [
        ('human', 'Human'),
        ('animal', 'Animal'),
        ('environmental', 'Environmental'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    symptoms = models.TextField(blank=True)
    severity = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.name} ({self.category})"


# -------------------------
# REPORTS (MAIN DASHBOARD DATA)
# -------------------------
class Report(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    date_reported = models.DateField(auto_now_add=True)
    number_of_cases = models.PositiveIntegerField()
    deaths = models.PositiveIntegerField(default=0)
    source = models.CharField(max_length=100, blank=True)
    reporter = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.disease.name} in {self.district.name}"


# -------------------------
# VOICE REPORTS (VOICE INPUT SYSTEM)
# -------------------------
class VoiceReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('added_to_dashboard', 'Added to Dashboard'),
    ]

    reporter = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='voice_reports/')
    transcribed_text = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Voice report by {self.reporter.user.username} - {self.status}"


