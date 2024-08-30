from django.urls import path

from cardmode import views

urlpatterns = [
    path('start/', views.study_view_start, name='cardmode'),
    path('web_app/<int:telegram_id>/', views.telegram_web_app_start, name='telegram_web_app_start'),
    path('get_similar_words/<str:telegram_id>/<str:mappings_id>/', views.SimilarWordsAPI.as_view(),
         name='get_similar_with_telegram_id'),
    path('get_similar_words/<str:mappings_id>/', views.SimilarWordsAPI.as_view(), name='get_similar_words'),
    path('get_hint/<str:telegram_id>/<str:mappings_id>/', views.GetHintAPI.as_view(), name='get_hint_with_telegram_id'),
    path('get_hint/<str:mappings_id>/', views.GetHintAPI.as_view(), name='get_hint'),
    path('get_sound/<str:mappings_id>/', views.GetSoundAPI.as_view(), name='get_sound'),
    path('get_card/<slug:slug>/<str:mode>/', views.GetCardAPIView.as_view(), name='get_card'),
    path('get_start_config/<str:telegram_id>/', views.GetStartConfigAPI.as_view(), name='get_start_config_tg'),
    path('get_start_config/<slug:slug>/<str:mode>/',
         views.GetStartConfigAPI.as_view(), name='get_start_config'),
    path('get_start_config/<slug:slug>/<str:mode>/<str:st_format>/',
         views.GetStartConfigAPI.as_view(), name='get_start_config_slug'),
    path('get_start_config/<slug:slug>/<str:mode>/<str:st_format>/<str:telegram_id>/',
         views.GetStartConfigAPI.as_view(), name='get_start_config_tg_slug'),
]
