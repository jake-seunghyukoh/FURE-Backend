
from django.urls import path
from . import views
 
app_name = 'api_plan'
urlpatterns = [
    path('', views.PlanView.as_view())
]