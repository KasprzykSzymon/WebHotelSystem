from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('lastminute/', views.last_minute, name='last_minute'),
    path('news/', views.news, name='news'),
    path('contact/', views.contact, name='contact'),
    path('signin/', views.sign_in, name='sign_in'),
    path('searchroom/', views.search_room, name='search_room'),

]
