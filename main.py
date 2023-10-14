import os
import telebot
import requests
import io
from dotenv import load_dotenv
from pydub import AudioSegment

from weather import process_user_message
from transcription import amazon_transcribe

load_dotenv()
TOKEN = os.getenv('TELEGRAM_API_KEY')


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(
        message.chat.id, "Hello! I'm WeatherAndVoiceTranscription bot. \n"
                         "You can ask me about the weather. \nOr send me "
                         "voice message, and I can Transcribe to text"
    )


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    result = process_user_message(message.text)
    bot.send_message(message.chat.id, result)


@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    file_id = message.voice.file_id

    file_info = bot.get_file(file_id)
    file_path = file_info.file_path

    voice_message_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
    voice_message = requests.get(voice_message_url)

    result = amazon_transcribe(voice_message.content)
    bot.send_message(message.chat.id, f'Here what you say: {result}')


bot.polling()
