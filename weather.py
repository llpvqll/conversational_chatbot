import requests
import spacy
import os
import gpt_2_simple as gpt2
from constants import (
    WEATHER_CONDITIONS,
    CLOSE_DATES,
    GPT2_MODEL_NAME,
    GPT2_STEPS,
)
from dotenv import load_dotenv

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


def fine_tune_gpt2(model_name, steps=200, run_name="my_chatbot"):
    gpt2.download_gpt2(model_name=model_name)
    sess = gpt2.start_tf_sess()
    gpt2.finetune(
        sess,
        dataset='data.txt',
        model_name=model_name,
        steps=steps,
        run_name=run_name
    )
    return sess


GPT2_SESSION = fine_tune_gpt2(GPT2_MODEL_NAME, GPT2_STEPS)


def generate_response(sess, model_name, user_input):
    gpt2.load_gpt2(sess, model_name=model_name)
    response = gpt2.generate(sess, model_name=model_name, prefix=user_input, return_as_list=True)[0]
    return response


def process_user_message(user_message):
    intent, location, date = parse_user_query(user_message)
    if intent == 'weather':
        response_message = get_weather(location, date)
    else:
        response_message = "I'm sorry, I couldn't understand your request."

    return generate_response(GPT2_SESSION, GPT2_MODEL_NAME, response_message)


def parse_user_query(query):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(query)

    intent = 'Sorry '
    location = None
    date = None

    for ent in doc.ents:
        if ent.label_ == 'GPE':
            location = ent.text
        if ent.label_ == 'DATE':
            date = ent.text

    for token in doc:
        if any(weather_condition.lower() in token.text.lower() for weather_condition in WEATHER_CONDITIONS):
            intent = 'weather'

    return intent, location, date


def get_weather(location, date):
    date, weather_base_url = _get_weather_url(location, date, WEATHER_API_KEY)
    response = requests.get(weather_base_url)

    if response.status_code == 200:
        current_weather_data = response.json().get('current')
        current_temperature = current_weather_data.get('temp')
        main_weather = current_weather_data.get('weather')[0].get('main')
        try:
            response_message = f"""
            The weather in {location.title()} on {date} is {main_weather} with a temperature of {_fahrenheit_to_celsius(current_temperature)}°C.
            """
        except (AttributeError, ValueError):
            return 'Sorry, I do not know city which you provided('
        return response_message
    else:
        return "Unable to retrieve weather information."


def _fahrenheit_to_celsius(fahrenheit_temp):
    return round(float((fahrenheit_temp - 32) * 5 / 9), 1)


def _get_weather_url(city, date, api_key):
    geocoding_url = f'https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=5&appid={api_key}'
    response = requests.get(geocoding_url).json()[0]
    if not date:
        date = 'today'
    if date.lower() in CLOSE_DATES.keys():
        date = CLOSE_DATES[date.lower()]
    return date, f'https://api.openweathermap.org/data/3.0/onecall?lat={response.get("lat")}&lon={response.get("lon")}&date={date.strftime("%Y-%m-%d")}&units=imperial&appid={api_key}'
