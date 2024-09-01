from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cards.models import Mappings
from cards.serializers import ImportCardsSerializer
from cards.services.handle_card_import import import_handler


class ImportCardsAPIView(APIView):
    """
    API view for importing cards into a specified category.
    """

    def post(self, request, slug, *args, **kwargs):
        """
        Handles the import of cards. Checks if the deck has more than 500 cards
        and if the import text is too long. If valid, processes the import.
        """
        serializer = ImportCardsSerializer(data=request.data)
        if serializer.is_valid():
            count = Mappings.objects.filter(category__slug=slug).count()

            # Restrict import if the deck has more than 500 cards and the input text is too long
            if count > 500 and len(serializer.validated_data['text']) > 400:
                return Response(
                    {'detail': 'Import isn\'t possible right now because the deck has over 500 cards. However, you can import the cards into other decks.'},
                    status=status.HTTP_405_METHOD_NOT_ALLOWED
                )

            # Process the import
            imports = import_handler(serializer.validated_data, slug)
            if imports:
                return Response({'detail': f'{imports} cards imported successfully'},
                                status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
