from django.urls import path
from . import views

app_name = "Generator"
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:request_id>/', views.detail, name='detail'),
    path('<int:request_id>/events/', views.events, name='events'),
]