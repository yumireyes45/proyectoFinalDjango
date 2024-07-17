from django.urls import path
from . import views
from home.dash_apps.finished_apps import dashProyecto

urlpatterns = [
    path('', views.loginfull, name='welcome'),
    path('dashboard/', views.Dashboard_view.as_view(), name='dashboard'),
]
