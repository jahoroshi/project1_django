from django.utils import timezone
from rest_framework import serializers

from cards.models import Categories
from users.models import User

class DeckSetSerializer(serializers.ModelSerializer):
    """
    Serializer for the Categories (Decks) model, including additional computed fields.
    """
    cards_count = serializers.IntegerField(read_only=True, required=False)
    reviews_count = serializers.IntegerField(required=False)
    new_cards_count = serializers.IntegerField(required=False)
    min_review_date = serializers.DateTimeField(required=False)
    telegram_id = serializers.IntegerField(required=False)

    class Meta:
        model = Categories
        fields = ('slug', 'name', 'cards_count', 'reviews_count', 'new_cards_count', 'min_review_date', 'telegram_id')

    def to_representation(self, instance):
        """
        Customize the representation of the serialized data to include the current time.
        """
        representation = super().to_representation(instance)
        representation['current_time'] = timezone.now()
        return representation

    def create(self, validated_data):
        """
        Handle the creation of a new deck, associating it with a user based on the Telegram ID.
        """
        telegram_id = validated_data.pop('telegram_id', None)
        user = User.objects.filter(telegram_id=telegram_id).first()
        validated_data['user'] = user
        return super().create(validated_data)


class DeckContentSerializer(serializers.Serializer):
    """
    Serializer for the content of a deck, representing individual card details.
    """
    side1 = serializers.CharField()
    side2 = serializers.CharField()
    card_id = serializers.IntegerField()
