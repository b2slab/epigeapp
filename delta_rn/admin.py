from django.contrib import admin
from .models import Sample, Classification, Calibration


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'status', 'email')
    list_filter = ('status', 'created')
    search_fields = ['email']


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ('sample', 'subgroup', 'probability_wnt', 'probability_shh', 'probability_gg')


@admin.register(Calibration)
class CalibrationAdmin(admin.ModelAdmin):
    list_display = ('sample', 'ROX_valid', 'FAM_valid', 'VIC_valid', 'amplification_test')
