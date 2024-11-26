from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePage, name='homePage'),
    path('lastminute/', views.lastMinute, name='lastMinute'),
    path('news/', views.news, name='news'),
    path('contact/', views.contact, name='contact'),
    path('signin/', views.signIn, name='signIn'),
    path('searchroom/', views.searchRoom, name='searchRoom'),

]
