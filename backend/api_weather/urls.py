from django.urls import path
from . import views
 
app_name = 'api_weather'
urlpatterns = [
    path('', views.WeatherView.as_view())
]