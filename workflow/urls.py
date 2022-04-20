from django.urls import path
from . import views

app_name = 'workflow'

urlpatterns = [
    path('upload_data/', views.analysis_view, name='upload_data'),
    path('admin/sample/<uuid:sample_id>/pdf/', views.admin_report_pdf, name='admin_report'),
]

