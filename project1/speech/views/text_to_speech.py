import datetime
import os

from django.conf import settings
from gtts import gTTS


def synthesize_speech(*args, **kwargs):
    """
    Synthesizes speech from text using Google Text-to-Speech (gTTS) and saves the output as an MP3 file.

    :param text: The text to be converted to speech. Defaults to 'Anki Chat'.
    :param lang: The language code for the speech synthesis (e.g., 'en' for English). Defaults to 'en'.
    :param card_id: A unique identifier for the card, used to name the output file.
    :return: The file path of the generated MP3 file.
    """
    text = kwargs.get('text', 'Anki Chat')
    lang = kwargs.get('lang', 'en')
    card_id = kwargs.get('card_id')

    # Construct the directory path based on the current date
    today = datetime.date.today()
    year = today.strftime('%Y')
    month = today.strftime('%m')
    day = today.strftime('%d')

    directory_path = os.path.join(settings.MEDIA_ROOT, 'text-to-speech', lang, year, month, day)
    os.makedirs(directory_path, exist_ok=True)  # Create the directory if it doesn't exist

    try:
        # Synthesize speech
        tts = gTTS(text=text, lang=lang)
        file_path = os.path.join(directory_path, f'card_{card_id}.mp3')
        tts.save(file_path)  # Save the synthesized speech to the file
    except ValueError as e:
        raise ValueError(f"Error in text-to-speech conversion: {str(e)}")

    return file_path
