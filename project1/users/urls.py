from django.urls import path, include
from rest_framework import routers

from users import views

app_name = 'users'

# Setting up a simple router for Telegram user management
router = routers.SimpleRouter()
router.register(r'tg', views.UserViewSet, basename='telegram_user')

urlpatterns = [
    path('login/', views.login, name='login'),  # Login view
    path('registration/', views.registration, name='registration'),  # Registration view
    path('profile/', views.profile, name='profile'),  # Profile management view
    path('logout/', views.logout, name='logout'),  # Logout view
    path('delete/', views.delete_user, name='delete'),  # User deletion view
    path('telegram/callback/', views.telegram_auth, name='telegram_auth'),  # Telegram authentication callback
    path('telegram-connect/', views.telegram_connect, name='telegram_connect'),  # Telegram account linking view
    path('manage/', include(router.urls)),  # Include router URLs for Telegram user management
    path('password/', views.second_step, name='second_step'),  # Second step login view
    path('', views.home, name='home'),  # Home view, serving as the entry point
]
