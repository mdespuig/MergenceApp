from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from datetime import datetime

class EmergencyReport(models.Model):
    HOTLINE_CHOICES = {
        'paramedics': 'A',
        'fire': 'B',
        'law': 'C',
        'utility': 'D',
    }

    ticket_id = models.CharField(max_length=20, unique=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports", null=True, blank=True)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    hotline_category = models.CharField(max_length=255)
    hotline_detail = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            year_suffix = datetime.now().strftime('%y')
            category_code = self.HOTLINE_CHOICES.get(self.hotline_category.lower(), 'X')
            last_count = EmergencyReport.objects.filter(created_at__year=datetime.now().year).count() + 1
            number = f"{last_count:03d}"
            self.ticket_id = f"MG-{year_suffix}{number}{category_code}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.name} {self.surname}"

class PartnerApplication(models.Model):
    HOTLINE_CATEGORIES = [
        ('paramedics', 'Paramedics'),
        ('fire', 'Fire & Rescue'),
        ('law', 'Law Enforcement'),
        ('utility', 'Utility & Electrical'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=100)
    address = models.TextField()
    hotline_number = models.CharField(max_length=20)
    hotline_category = models.CharField(max_length=20, choices=HOTLINE_CATEGORIES)
    date_submitted = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.organization_name} ({self.get_hotline_category_display()})"

class Hotline(models.Model):
    organization_name = models.CharField(max_length=255)
    hotline_type = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    hotline_number = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.organization_name} ({self.hotline_type})"

class TimelineUpdates(models.Model):
    report = models.ForeignKey(
        EmergencyReport,
        on_delete=models.CASCADE,
        related_name='timeline_updates'
    )
    ticket_id = models.CharField(max_length=20, null=True, editable=False)
    title = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=now)
    responder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.report:
            self.ticket_id = self.report.ticket_id
            
            try:
                partner_app = PartnerApplication.objects.get(
                    hotline_category=self.report.hotline_category,
                    organization_name=self.report.hotline_detail
                )
                self.responder = partner_app.user
            except PartnerApplication.DoesNotExist:
                self.responder = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.title}"
