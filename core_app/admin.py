from django.contrib import admin
from .models import Sample
from django.urls import reverse
from django.utils.safestring import mark_safe


def report_pdf(obj):
    url = reverse('core_app:admin_report_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')


report_pdf.short_description = 'Report'


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'sample_identifier', 'diagnosis', 'created', 'status', report_pdf)
