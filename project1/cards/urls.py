from django.urls import path
from . import views

# from views import add_card

urlpatterns = [
    path(
        '<slug:slug>/create/',
        views.CardCreateView.as_view(),
        name="card_create",
    ),
    path(
        'new-card/',
        views.CardCreateView.as_view(),
        name="card_create",
    ),

    path(
        'edit/<int:pk>/',
        views.CardUpdateView.as_view(),
        name="card_edit",
    ),
    path(
        'edit/<slug:slug>/<int:pk>/',
        views.CardUpdateView.as_view(),
        name="card_edit",
    ),



    path("", views.DecksListView.as_view(), name="decks_list"),

    path("deck/new/", views.DeckCreateView.as_view(), name="deck_create"),

    # path("deck/delete/<int:pk>/", views.DeckDeleteView.as_view(), name="deck_delete"),
    path("deck/delete/<int:pk>/", views.deck_delete, name="deck_delete"),

    path("deck/<slug:slug>/delete/<int:pk>/", views.CardDeleteView.as_view(), name="card_delete"),

    path("deck/rename/<int:pk>/", views.DeckUpdateView.as_view(), name="deck_edit"),

    path("learn/<slug:slug>/", views.BoxView.as_view(), name="learn_cards"),

    path("deck/<slug:slug>/", views.CardsListView.as_view(), name="deck_content"),

    path("deck/<slug:slug>/import/", views.import_cards, name="import_cards"),

    path("learn/<slug:slug>/<int:rep>/", views.BoxView.as_view(), name="learn_cards_rep"),

    path("test_contact/", views.test_contact, name="test_contact"),
]
