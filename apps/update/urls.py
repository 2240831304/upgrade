

from django.urls import path
from update import views


urlpatterns = [
    path('servertest/', views.serverTest),
    path('updatetest',views.upgradeTest),
    path('update',views.CheckVersion),
    path('main',views.MainPageView.as_view())
]
