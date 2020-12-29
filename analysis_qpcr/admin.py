from django.contrib import admin
from .models import Sample


@admin.register(Sample)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('submit_date', 'file')