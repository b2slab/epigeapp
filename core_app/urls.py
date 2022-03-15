from django.urls import path
from . import views

app_name = 'core_app'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('instructions/', views.instructions_view, name='instructions'),
    path('upload_file/', views.analysis_view, name='analysis'),
    path('success/', views.success_view, name='success'),
    path('terms_and_conditions/', views.terms_view, name='terms'),
    path('data_policy/', views.privacy_view, name='privacy'),
    path('legal_notice/', views.legal_view, name='legal'),
    path('funding/', views.funding_view, name='funding'),
    path('admin/sample/<uuid:sample_id>/pdf/', views.admin_report_pdf, name='admin_report_pdf'),
    path('protocols/', views.protocols_view, name='protocols'),
    path('download/<filename>/', views.download_pdf, name='download'),
]
