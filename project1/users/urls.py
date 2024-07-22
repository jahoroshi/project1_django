from django.urls import path, include
from rest_framework import routers

from users import views

app_name = 'users'

router = routers.SimpleRouter()
router.register(r'manage', views.UserViewSet, basename='telegram_user')
print(router.urls)

urlpatterns = [
    path('login/', views.login, name='login'),
    path('registration/', views.registration, name='registration'),
    path('prifile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path('api/v1/', include(router.urls)),
]