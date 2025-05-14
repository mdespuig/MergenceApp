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
