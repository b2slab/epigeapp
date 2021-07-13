from django.urls import path
from . import views

app_name = 'delta_rn'

urlpatterns = [
    path('analysis_delta_rn/', views.analysis_view, name='analysis'),
]
