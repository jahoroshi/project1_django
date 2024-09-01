"""
URL configuration for the project_1 project.

The `urlpatterns` list routes URLs to views. For more information, see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/

Examples:
Function views:
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')

Class-based views:
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')

Including another URLconf:
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    # Admin path
    path('admin/', admin.site.urls),

    # App-specific paths
    path('cards/', include("cards.urls")),
    path('speech/', include("speech.urls")),
    path('deck/', include("deckhub.urls")),
    path('study/', include("cardmode.urls")),
    path('users/', include("users.urls", namespace='users')),

    # API version 1 paths
    path('api/v1/cards/', include("cards.urls")),
    path('api/v1/speech/', include("speech.urls")),
    path('api/v1/deck/', include("deckhub.urls")),
    path('api/v1/study/', include("cardmode.urls")),
    path('api/v1/users/', include("users.urls", namespace='users-api')),

    # Fallback to user URLs
    path('', include("users.urls")),
]

# Include debug toolbar URLs only in DEBUG mode
urlpatterns += debug_toolbar_urls()

# Serve static and media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
