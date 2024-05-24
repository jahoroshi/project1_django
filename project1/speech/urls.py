from django.urls import path
from speech import views

urlpatterns = [
    path('tts/<str:mappings_id>', views.synthesize_speech, name='get_speech'),
]