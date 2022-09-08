from django.urls import path
from . import views

app_name = 'core_app'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('instructions/', views.instructions_view, name='instructions'),
    path('success/', views.success_view, name='success'),
    # path('terms_and_conditions/', views.terms_view, name='terms'),
    # path('data_policy/', views.privacy_view, name='privacy'),
    # path('legal_notice/', views.legal_view, name='legal'),
    # path('funding/', views.funding_view, name='funding'),
    path('protocols/', views.protocols_view, name='protocols'),
    path('contact/', views.contact_view, name='contact'),
    path('information/', views.information_view, name='information'),
    path('download/<filename>/', views.download_pdf, name='download'),
    path('about_us/', views.about_view, name='about'),
    path('search_job/', views.search_view, name='search-job'),
    path('sample/<uuid:sample_id>/', views.sample_view, name='sample-detail'),
]
