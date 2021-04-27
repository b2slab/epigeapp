from django.contrib import admin
from .models import Sample, Classification, Calibration
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


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ('sample', 'subgroup1', 'score1', 'distLab1', 'subgroup2', 'score2', 'distLab2')


@admin.register(Calibration)
class CalibrationAdmin(admin.ModelAdmin):
    list_display = ('sample', 'ROX_valid', 'FAM_valid', 'VIC_valid', 'amplification_test')
