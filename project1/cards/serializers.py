from rest_framework import serializers
from cards.models import Cards


class ImportCardsSerializer(serializers.Serializer):
    """
    Serializer for importing cards with custom separators.
    """
    text = serializers.CharField()
    words_separator = serializers.CharField()
    cards_separator = serializers.CharField()
    words_separator_custom = serializers.CharField(required=False, allow_blank=True)
    cards_separator_custom = serializers.CharField(required=False, allow_blank=True)


class CardSetSerializer(serializers.ModelSerializer):
    """
    Serializer for representing a set of cards, focusing on the basic fields.
    """
    class Meta:
        model = Cards
        fields = ['side1', 'side2']


class CardCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new card, with optional fields for managing two sides and a slug.
    """
    is_two_sides = serializers.BooleanField(required=False)
    slug = serializers.SlugField()
    side1 = serializers.CharField(required=False)
    side2 = serializers.CharField(required=False)

    class Meta:
        model = Cards
        fields = ['side1', 'side2', 'is_two_sides', 'slug']
