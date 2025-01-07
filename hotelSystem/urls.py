from django.urls import path
from . import views
from .views import process_payment, payment_success, payment_cancel  # Dodajemy import widoku process_payment

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home_page_view, name='home_page'),
    path('lastminute/', views.last_minute_view, name='last_minute'),
    path('news/', views.news_view, name='news'),
    path('contact/', views.contact_view, name='contact'),
    path('signin/', views.sign_in_view, name='sign_in'),
    path('searchroom/', views.search_room_view, name='search_room'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('edit_profile/', views.edit_profile_view, name='edit_profile'),
    path('logout', views.logout_view, name='logout'),
    path('contact/logout', views.logout_view),
    path('news/logout', views.logout_view),
    path('searchroom/logout', views.logout_view),
    path('lastminute/logout', views.logout_view),
    path('profile/logout', views.logout_view),
    path('edit_profile/logout', views.logout_view),
    path('rooms/', views.room_list, name='room_list'),
    path('room/<int:pk>/', views.room_detail, name='room_detail'),
    path('room/<int:pk>/reserve/', views.make_reservation, name='make_reservation'),
    path('process_payment/<int:room_id>/', process_payment, name='process_payment'),
    path('payment_success/<int:room_id>/', payment_success, name='payment_success'),
    path('payment_cancel/', payment_cancel, name='payment_cancel'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
