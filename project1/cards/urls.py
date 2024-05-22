from django.urls import path

from cards import views

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
    path('get_card/', views.get_card, name='get_card'),
    path('get_card/<slug:slug>/', views.get_card, name='get_card'),
    path('show_back/<int:card_id>/', views.show_back, name='show_back'),
    path('get_similar_words/<str:mappings_id>/', views.get_similar_words, name='get_similar_words'),
    path('get_hint/<int:card_id>/', views.get_hint, name='get_hint'),
    path('submit_answer/<int:card_id>/', views.submit_answer, name='submit_answer'),
    path('study/<slug:slug>/<int:rep>/', views.study_view, name='study'),
    path('study/<slug:slug>/', views.study_view, name='study'),
    path('study/', views.study_view, name='study'),
]
