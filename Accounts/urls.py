from django.urls import path
from django.contrib.auth import views as auth_views
from .views import signup_view

app_name = 'accounts'
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name="Accounts/login.html"), name="login"),
    path('signup/', signup_view, name="signup"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
]