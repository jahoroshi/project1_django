from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.urls import reverse

from cards.forms import ImportCardsForm
from cards.models import Categories, Cards, Mappings
from cards.serializers import ImportCardsSerializer
from cards.services.handle_card_import import import_handler
# from cards.permissions import check_permission_with_slug


class ImportCardsAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, slug, *args, **kwargs):
        serializer = ImportCardsSerializer(data=request.data)
        if serializer.is_valid():
            count = Mappings.objects.filter(category__slug=slug).count()
            if count > 500 and len(serializer.validated_data['text']) > 600:
                return Response(
                    {'detail': 'Import not allowed: The category contains more than 500 cards.'},
                    status=status.HTTP_405_METHOD_NOT_ALLOWED
                )
            imports = import_handler(serializer.validated_data, slug)
            if imports:
                return Response({'detail': f'{imports} cards imported successfully'},
                                status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)


