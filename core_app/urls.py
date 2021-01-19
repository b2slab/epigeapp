from django.urls import path
from . import views

app_name = 'core_app'

urlpatterns = [
    path('', views.instructions_view, name='instructions'),
    path('upload_file/', views.analysis_view, name='analysis'),
]
