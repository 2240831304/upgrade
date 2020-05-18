

from django.urls import path
from update import views


urlpatterns = [
    path('servertest/', views.serverTest),
    path('update',views.CheckVersion)
]
