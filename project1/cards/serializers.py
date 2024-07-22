from rest_framework import serializers

from cards.models import Cards


class ImportCardsSerializer(serializers.Serializer):
    text = serializers.CharField()
    words_separator = serializers.CharField()
    cards_separator = serializers.CharField()
    words_separator_custom = serializers.CharField(required=False, allow_blank=True)
    cards_separator_custom = serializers.CharField(required=False, allow_blank=True)


class CardSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cards
        fields = ['side1', 'side2']


class CardCreateSerializer(serializers.ModelSerializer):
    is_two_sides = serializers.BooleanField(required=False)
    slug = serializers.SlugField()
    side1 = serializers.CharField(required=False)
    side2 = serializers.CharField(required=False)

    class Meta:
        model = Cards
        fields = ['side1', 'side2', 'is_two_sides', 'slug']
