from django.urls import path
from . import views

app_name = 'workflow'

urlpatterns = [
    path('upload_data/', views.workflow_view, name='upload_data'),
    path('sample/<uuid:sample_id>/pdf/', views.download_report, name='download_report'),
    path('admin/sample/<uuid:sample_id>/pdf/', views.admin_report_pdf, name='admin_report'),
]

