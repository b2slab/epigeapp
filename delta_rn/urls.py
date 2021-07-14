from django.urls import path
from . import views

app_name = 'delta_rn'

urlpatterns = [
    path('analysis_delta_rn/', views.analysis_view, name='analysis'),
    path('admin/delta_rn_sample/<uuid:sample_id>/pdf/', views.admin_report_pdf, name='admin_report_delta_rn'),
]
