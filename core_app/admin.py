from django.contrib import admin
from .models import Sample, QualityControl
from django.urls import reverse
from django.utils.safestring import mark_safe


def report_pdf(obj):
    url = reverse('core_app:admin_report_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')


report_pdf.short_description = 'Report'


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'status', 'email', report_pdf)
    list_filter = ('status', 'created')
    search_fields = ['email']


admin.site.register(QualityControl)
