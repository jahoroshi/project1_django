from django.urls import path, include

from cards import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'manage', views.CardViewSetApi, basename='cards')
print(router.urls)

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
    path("<slug:slug>/import/", views.import_cards, name="import_cards"),
    path("<slug:slug>/delete/<int:pk>/", views.CardDeleteView.as_view(), name="card_delete"),
    path('api/v1/import_cards/<slug:slug>/', views.ImportCardsAPIView.as_view(), name='import_cards_api'),
    # path('api/v1/create/<slug:slug>/<int:pk>/', views.CardViewSetApi.as_view({'post': 'create'})),
    path('api/v1/', include(router.urls)),

]
