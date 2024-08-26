from django.urls import path, include
from rest_framework import routers

from users import views

app_name = 'users'

router = routers.SimpleRouter()
router.register(r'tg', views.UserViewSet, basename='telegram_user')
print(router.urls)

urlpatterns = [
    path('login/', views.login, name='login'),
    path('registration/', views.registration, name='registration'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path('delete/', views.delete_user, name='delete'),
    path('telegram/callback/', views.telegram_auth, name='telegram_auth'),
    path('telegram-connect/', views.telegram_connect, name='telegram_connect'),
    path('manage/', include(router.urls)),
    path('password/', views.second_step, name='second_step'),
    path('', views.home, name='home'),
]