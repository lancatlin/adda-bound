from django.urls import path
from bot import views


urlpatterns = [
    path('line', views.line_endpoint, name='line-endpoint'),
]
