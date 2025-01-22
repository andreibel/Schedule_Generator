from django.urls import path
from . import views

app_name = "Generator"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:schedule_id>/', views.detail, name='detail'),
    path('<int:schedule_id>/events/', views.events, name='events'),
]