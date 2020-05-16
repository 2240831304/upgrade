

from django.urls import path
from update import views


urlpatterns = [
    path('updatetest/', views.updateTest),
    path('update',views.CheckVersion)
]
