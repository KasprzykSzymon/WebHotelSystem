from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('lastminute/', views.last_minute, name='last_minute'),
    path('news/', views.news, name='news'),
    path('contact/', views.contact, name='contact'),
    path('signin/', views.sign_in, name='sign_in'),
    path('searchroom/', views.search_room, name='search_room'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('logout', views.logout_view),
    path('contact/logout', views.logout_view),
    path('news/logout', views.logout_view),
    path('searchroom/logout', views.logout_view),
    path('lastminute/logout', views.logout_view),
    path('profile/logout', views.logout_view),
    path('edit_profile/logout', views.logout_view)

]