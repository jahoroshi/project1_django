from django.urls import path, include
from rest_framework import routers

from cards import views

# Initialize the router and register the CardViewSetApi
router = routers.SimpleRouter()
router.register(r'manage', views.CardViewSetApi, basename='cards')

urlpatterns = [
    # URL pattern for creating a new card, with an optional slug parameter
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

    # URL patterns for editing an existing card
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

    # URL pattern for importing cards to a specific deck/category
    path("<slug:slug>/import/", views.import_cards, name="import_cards"),

    # URL pattern for deleting a specific card from a deck/category
    path("<slug:slug>/delete/<int:pk>/", views.CardDeleteView.as_view(), name="card_delete"),

    # API endpoint for importing cards
    path('import_cards/<slug:slug>/', views.ImportCardsAPIView.as_view(), name='import_cards_api'),

    # Include the router's URLs, which handle management of cards through the API
    path('', include(router.urls)),
]
