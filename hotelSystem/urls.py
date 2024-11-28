from django.urls import path
from . import views

urlpatterns = [
    path('last_minute/', views.last_minute, name='last_minute'),
    path('news/', views.news, name='news'),
    path('contact/', views.contact, name='contact'),
    path('sign_in/', views.sign_in, name='sign_in'),
    path('search_room/', views.search_room, name='search_room'),
    path('', views.home_page, name='home_page'),

]