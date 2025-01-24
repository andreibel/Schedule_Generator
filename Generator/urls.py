# Generator/urls.py

from django.urls import path
from .views import IndexView, detail, events, CreateScheduleView

app_name = 'generator'  # Defines the namespace

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('schedule/create/', CreateScheduleView.as_view(), name='create_schedule'),
    path('details/<int:schedule_id>/', detail, name='detail'),
    path('events/<int:schedule_id>/', events, name='events'),
]