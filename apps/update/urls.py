

from django.urls import path
from update import views


app_name = 'update'
urlpatterns = [
    path('servertest/', views.serverTest),
    path('updatetest',views.upgradeTest),
    path('update',views.CheckVersion),
    path('main',views.MainPageView.as_view(), name='main'),
    path('pushlishtest',views.PushlisVersionTestView.as_view(),name='pushlishtest'),
    path('publishversion',views.PublishVersionView.as_view(),name="publishversion"),
    path('managerversion',views.VersionManagerView.as_view(),name="managerversion"),
    path('publishnewstest',views.HandlePublishNewsTest),
    path('publishnews',views.HandlePublishNews),
    path('upgradepackage',views.HandlePackage),
    path('versionmanagesys',views.VersionManageSys),
]
