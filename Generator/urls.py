# Generator/urls.py

from django.urls import path
from . import views

app_name = 'generator'  # Defines the namespace

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('schedule/create/', views.CreateScheduleView.as_view(), name='create_schedule'),
    path('details/<int:schedule_id>/', views.detail, name='detail'),
    path("generate/<int:schedule_id>/",views.generate_combinations_view , name='generate_combinations'),
    path('events/<int:schedule_id>/', views.events, name='events'),
    path('calendar/<int:schedule_id>/', views.weekly_calendar_view, name='weekly_calendar'),
]