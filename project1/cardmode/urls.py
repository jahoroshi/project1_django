from django.urls import path

from cardmode import views

urlpatterns = [
    path('<slug:slug>/', views.study_view_start, name='cardmode'),
    path('get_similar_words/<str:mappings_id>/', views.SimilarWordsAPI.as_view(), name='get_similar_words'),
    path('get_hint/<str:mappings_id>/', views.GetHintAPI.as_view(), name='get_hint'),
    path('get_sound/<str:mappings_id>/', views.GetSoundAPI.as_view(), name='get_sound'),
    path('get_card/<slug:slug>/<str:mode>/', views.GetCardAPIView.as_view(), name='get_card'),
    path('get_start_config/<str:telegram_id>/', views.GetStartConfigAPI.as_view(), name='get_start_config_tg'),
    path('get_start_config/<slug:slug>/<str:mode>/',
         views.GetStartConfigAPI.as_view(), name='get_start_config'),
    path('get_start_config/<slug:slug>/<str:mode>/<str:st_format>/<str:telegram_id>/',
         views.GetStartConfigAPI.as_view(), name='get_start_config_tg_slug'),
]
