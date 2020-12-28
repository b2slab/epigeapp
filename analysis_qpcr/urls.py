from django.urls import path
from . import views

app_name = 'analysis_qpcr'

urlpatterns = [
    path('', views.main_view, name='main'),
]
