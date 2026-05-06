from django.urls import path
from .views import HomeView, RobotsTxtView

app_name = 'home'

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('robots.txt', RobotsTxtView.as_view(), name='robots_txt'),
]
