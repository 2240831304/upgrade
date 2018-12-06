from django.urls import path

from apps.user.views import LoginView, LogoutView

app_name = 'user'
urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('', LoginView.as_view()),
    path('index.html', LoginView.as_view()),
]
