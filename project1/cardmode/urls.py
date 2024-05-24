from django.urls import path

from cardmode import views

urlpatterns = [
    path('<slug:slug>/', views.study_view, name='cardmode'),
    path('get_card/', views.get_card, name='get_card'),
    path('get_card/<slug:slug>/', views.get_card, name='get_card'),
    path('get_similar_words/<str:mappings_id>/', views.get_similar_words, name='get_similar_words'),
    path('get_hint/<str:mappings_id>/', views.get_hint, name='get_hint'),
    path('submit_answer/<int:card_id>/', views.submit_answer, name='submit_answer'),
    path('get_sound/<str:mappings_id>', views.get_sound, name='get_sound'),
]
