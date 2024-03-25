import json
import boto3
import wave
from pydub import AudioSegment
import os
import io
import tempfile

translator = boto3.client(service_name='translate')
polly = boto3.client("polly") 
s3 = boto3.resource('s3')


def lambda_handler(event, context):
    # TODO implement
    bucket_name = os.environ['bucketname'] # format bucketname / 
    cloudfronturl = os.environ['cloudfronturl']
    text = event["queryStringParameters"]["txt"]
    sourceLanguage = event["queryStringParameters"]["sourceLanguageCode"]
    targetLanguage = event["queryStringParameters"]["targetLanguageCode"]
    contactId = event["queryStringParameters"]["contactId"]
    bucket = s3.Bucket(bucket_name)
    #Initializing variables
    CHANNELS = 1 #Polly's output is a mono audio stream
    RATE = 8000 #Polly supports 16000Hz and 8000Hz output for PCM format
    OUTPUT_FILE_IN_WAVE = "/tmp/"+contactId+".wav" #WAV format Output file  name
    #OUTPUT_FILE_IN_WAVE = tmp = ou.NamedTemporaryFile(delete=True)  #WAV format Output file  name
    FRAMES = []
    WAV_SAMPLE_WIDTH_BYTES = 2 # Polly's output is a stream of 16-bits (2 bytes) samples

    print('translating from',sourceLanguage,'to',targetLanguage)
    #we pick a random voice
    voices = polly.describe_voices(LanguageCode=targetLanguage)
    voiceId = voices['Voices'][0]['Id']
    result = translator.translate_text(Text=text, SourceLanguageCode = sourceLanguage,TargetLanguageCode=targetLanguage)
    r = polly.synthesize_speech(
        Text = result.get('TranslatedText'),
        OutputFormat = 'pcm',
        LanguageCode = targetLanguage,
        SampleRate = '8000',
        VoiceId = voiceId
    )
    #Processing the response to audio stream
    STREAM = r.get("AudioStream")
    FRAMES.append(STREAM.read())
    
    WAVEFORMAT = wave.open(OUTPUT_FILE_IN_WAVE,'wb')
    WAVEFORMAT.setnchannels(CHANNELS)
    WAVEFORMAT.setsampwidth(WAV_SAMPLE_WIDTH_BYTES)
    WAVEFORMAT.setframerate(RATE)
    WAVEFORMAT.writeframes(b''.join(FRAMES))
    WAVEFORMAT.close()
    
    finalfile = io.BytesIO()
    track = AudioSegment.from_wav(OUTPUT_FILE_IN_WAVE)
    track.export(finalfile, format='wav',codec="pcm_mulaw" ,parameters=['-ar', '8000'] )
    finalfile.seek(0)
    s3.Object(bucket_name,'customerprompts/'+contactId+'.wav').upload_fileobj(finalfile)
    return {
        'statusCode': 200,
         'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': cloudfronturl, 
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        #'body': result.get('TranslatedText')
        'body' : len(track)
        
    }
