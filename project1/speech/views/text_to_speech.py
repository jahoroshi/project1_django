from django.contrib.auth.decorators import login_required
from gtts import gTTS
from django.conf import settings
import os
import datetime
@login_required
def synthesize_speech(*args, **kwargs):
    text = kwargs.get('text', 'Anki Chat')
    lang = kwargs.get('lang', 'en')
    card_id = kwargs.get('card_id')

    today = datetime.date.today()
    year = today.strftime('%Y')
    month = today.strftime('%m')
    day = today.strftime('%d')

    directory_path = os.path.join(settings.MEDIA_ROOT, 'text-to-speech', lang, year, month, day)
    os.makedirs(directory_path, exist_ok=True)

    try:
        tts = gTTS(text=text, lang=lang)
        file_path = os.path.join(directory_path, f'card_{card_id}.mp3')
        tts.save(file_path)
    except ValueError as e:
        raise ValueError(f"Speech-app -->>  Error in text-to-speech conversion: {str(e)}")

    return file_path




