from django.urls import path

from deckhub import views

urlpatterns = [
    path("new/", views.DeckCreateView.as_view(), name="deck_create"),
    path("delete/<slug:slug>/", views.deck_delete, name="deck_delete"),
    path("rename/<int:pk>/", views.DeckUpdateView.as_view(), name="deck_edit"),
    path("<slug:slug>/", views.DeckContentView.as_view(), name="deck_content"),
    path('', views.DecksListView.as_view(), name="decks_list"),
]
