import boto3
import os
import requests
from time import sleep

from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv


load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')


def save_voice_to_s3(file_obj, file_name):
    try:
        with open(file_name, 'wb') as file:
            file.write(file_obj)
        s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_DEFAULT_REGION
        )
        s3.upload_file(file_name, AWS_STORAGE_BUCKET_NAME, file_name, ExtraArgs={'ContentType': 'audio/mpeg'})
        s3_url = f's3://{AWS_STORAGE_BUCKET_NAME}/{file_name}'
        return s3_url
    except NoCredentialsError:
        return "AWS credentials are missing or incorrect."
    except Exception as e:
        return f"Error: {str(e)}"


def amazon_transcribe(audio_file_obj, max_speakers=2):
    transcribe = boto3.client(
        'transcribe',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )
    try:
        if max_speakers > 10:
            raise ValueError("Maximum detected speakers is 10.")

        file_name = 'audio.mp3'
        print('hello before save voice method')
        job_uri = save_voice_to_s3(audio_file_obj, file_name)
        print('hello after save voice method')
        job_name = str(file_name.split('.')[0])

        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat='ogg',
            LanguageCode='en-US',
            Settings={
                'ShowSpeakerLabels': True,
                'MaxSpeakerLabels': max_speakers
            }
        )
        while True:
            result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            if result['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            sleep(5)
        if result['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            data = requests.get(result['TranscriptionJob']['Transcript']['TranscriptFileUri']).json()
            transcribe.delete_transcription_job(TranscriptionJobName=job_name)
            return data['results']['transcripts'][0]['transcript']
        transcribe.delete_transcription_job(TranscriptionJobName=job_name)
        return "I can't transcript your voice message."
    except transcribe.exceptions.ConflictException:
        boto3.client('transcribe').delete_transcription_job(TranscriptionJobName='audio')
        return "Oops, I forgot what you say 😥. Please send this message again"
