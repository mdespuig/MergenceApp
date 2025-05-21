from django.contrib import admin
from .models import EmergencyReport

@admin.register(EmergencyReport)
class EmergencyReportAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'name', 'surname', 'hotline_category', 'hotline_detail', 'created_at')
    ordering = ('-created_at',)
