from django.urls import path, include
from rest_framework import routers

from deckhub import views

urlpatterns = [
    path("new/", views.DeckCreateView.as_view(), name="deck_create"),
    path("delete/<slug:slug>/", views.deck_delete, name="deck_delete"),
    path("rename/<int:pk>/", views.DeckUpdateView.as_view(), name="deck_edit"),
    path("content/<slug:slug>/", views.DeckContentView.as_view(), name="deck_content"), # !!!!!! решить конфликт с последним



    path('manage/', views.DeckViewSetApi.as_view({'get': 'list', 'post': 'create'}), name='deck_list'),
    path('manage/list/<int:tg_user>/', views.DeckViewSetApi.as_view({'get': 'list'}), name='decks_list_tguser'),
    path('manage/<slug:slug>/', views.DeckViewSetApi.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='deck-detail'),
    path('manage/reset/<int:tg_user>/<slug:slug>/', views.reset_deck_progress, name='decks_list_tguser'),
    path('manage/<int:tg_user>/<slug:slug>/', views.DeckContentViewApi.as_view({'get': 'list'}), name='deck_content_tguser'),
    path('manage/first_filling/<int:tg_user>/<str:language>', views.first_deck_fill, name='first_deck_fill'),
    path('', views.DecksListView.as_view(), name="decks_list"),
]
