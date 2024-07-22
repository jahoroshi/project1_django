from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response

from cards.models import Cards, Categories, Mappings
from cards.serializers import CardSetSerializer, CardCreateSerializer


class CardViewSetApi(viewsets.ModelViewSet):
    # queryset = Cards.objects.all()
    # permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'destroy'):
            return CardCreateSerializer
        return CardSetSerializer

    def get_queryset(self):
        # if self.action ==
        serializers = self.get_serializer(data=self.request.data)
        serializers.is_valid(raise_exception=True)
        valid_data = serializers.validated_data
        mappings = Mappings.objects.filter(category__slug=valid_data.get('slug'))
        queryset = Cards.objects.filter(id__in=mappings.values('card_id'))
        return queryset


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        valid_data = serializer.validated_data
        slug = valid_data.get('slug')
        category = get_object_or_404(Categories, slug=slug)
        card = Cards.objects.create(
            side1=valid_data['side1'],
            side2=valid_data['side2']
        )

        Mappings.objects.create(card=card, category=category)

        if valid_data['is_two_sides'] is True:
            Mappings.objects.create(card=card, category=category, is_back_side=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        serializer.save()
        if serializer.validated_data['is_two_sides'] is True:
            count = Mappings.objects.filter(card=serializer.instance).count()
            if count == 1:
                category = get_object_or_404(Categories, slug=serializer.validated_data['slug'])
                Mappings.objects.create(card=serializer.instance, category=category, is_back_side=True)
