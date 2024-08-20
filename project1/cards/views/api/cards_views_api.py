from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response

from cards.models import Cards, Categories, Mappings
from cards.serializers import CardSetSerializer, CardCreateSerializer
from cards.services.second_side_creator import create_second_side


class CardViewSetApi(viewsets.ModelViewSet):
    # queryset = Cards.objects.all()
    # permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'destroy'):
            return CardCreateSerializer
        return CardSetSerializer

    def get_queryset(self):
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
        side1 = valid_data['side1']
        side2 = valid_data['side2']
        card = Cards.objects.create(
            side1=side1,
            side2=side2,
        )

        mapping_object = Mappings.objects.create(card=card, category=category)

        if valid_data.get('is_two_sides') is True:
            create_second_side(category, mapping_object, side1=side1, side2=side2)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        serializer.save()
        if serializer.validated_data['is_two_sides'] is True:
            mapping_object = get_object_or_404(Mappings, card=serializer.instance)
            if mapping_object.has_two_sides is False:
                category = get_object_or_404(Categories, slug=serializer.validated_data['slug'])
                side1 = serializer.instance.side1
                side2 = serializer.instance.side2
                create_second_side(category, mapping_object, side1=side1, side2=side2)
