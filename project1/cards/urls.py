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

    # path("deckhub/delete/<int:pk>/", views.DeckDeleteView.as_view(), name="deck_delete")
    # path("learn/<slug:slug>/", views.BoxView.as_view(), name="learn_cards"),
    # path("learn/<slug:slug>/<int:rep>/", views.BoxView.as_view(), name="learn_cards_rep"),
    path("<slug:slug>/import/", views.import_cards, name="import_cards"),
    path("<slug:slug>/delete/<int:pk>/", views.CardDeleteView.as_view(), name="card_delete"),
    # path('study/<slug:slug>/<int:rep>/', views.study_view, name='study'),
    # path('study/<slug:slug>/', views.study_view, name='study'),
    # path('study/', views.study_view, name='study'),
]
