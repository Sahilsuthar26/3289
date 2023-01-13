# !pip install --upgrade azure-cognitiveservices-speech

import requests
from azure.storage.blob import BlobServiceClient, BlobClient
import os
import json
import logging

AzureWebJobsStorage = "DefaultEndpointsProtocol=https;AccountName=storageaccounttransbf73;AccountKey=PY8qbZmul63QhbPc5drNzrDIZPl0lEzITFGoVmx5JpYQrEQfaPI4XMYUYhrvuwpZfXc4PA1BIscxDDiLXlsDrw==;EndpointSuffix=core.windows.net"
FUNCTIONS_WORKER_RUNTIME = "python"
SAS_TOKEN = "?sv=2020-08-04&ss=bfqt&srt=sco&sp=rwlacx&se=2025-01-18T10:58:49Z&st=2022-01-18T02:58:49Z&spr=https,http&sig=%2FO9R58iNjTnUSnSYCH4IpgdXPzmxQdL9qPGr5Wv97Ao%3D"
TRANSLATION_KEY = "deafc18699e6416b9b343cd63a46fd5f"
TRANSLATION_MODEL_CATEGORY = "64f12deb-a8ed-438a-8b90-da5ac38c77a8-TECH"
TRANSLATE_EXCEL_FUNCTION_URL = "https://translationfunctionnwk.azurewebsites.net/api/TranslateExcelDoc?code=6Xbty2Ibv5mSTGvpPL0ff563LG44As1HV9LShbUZ5QiK1IXAPxmAdQ=="
translationdocsstorage_STORAGE = "DefaultEndpointsProtocol=https;AccountName=translationdocsstorage;AccountKey=egY1GMShp6xdYffTUdRySOc1MMzF6n39xk1TCNYZUUugxCKqBbNO1Y/43HA468rDbEwf/hL/Vlr5e+Rz05Qk6Q==;EndpointSuffix=core.windows.net"
TRANSLATION_TABLE_NAME = "translationdocsstorage"
TRANSLATION_TABLE_KEY = "egY1GMShp6xdYffTUdRySOc1MMzF6n39xk1TCNYZUUugxCKqBbNO1Y/43HA468rDbEwf/hL/Vlr5e+Rz05Qk6Q=="
SPEECH_KEY = "4c27b881b50a46abaad5385a18d51ead"
SPEECH_REGION = "eastus2"
TRANSLATE_WAV_FUNCTION_URL = "https://translatorfunctionnwkv2.azurewebsites.net/api/TranslateWavFile?code=PZc2hEh4K1HngNBluF5W/NFSHVGhAJsOyvbxF9flXcaldVdGuO5RRA=="
STORAGE_ACCOUNT_URL = "https://translationdocsstorage.blob.core.windows.net/"
UPLOAD_STORAGE_ACCOUNT_URL = "https://azcdsstoragefapp01d.blob.core.windows.net/"
blob_sas = "sp=r&st=2022-11-02T09:47:46Z&se=2025-12-31T17:47:46Z&spr=https&sv=2021-06-08&sr=c&sig=oeyh0YLTL4%2FjDNYsEwGxkkCx2YfKwY%2Bae%2F8OpNCDzX4%3D"
storage_account_name = 'azcdsstoragefapp01d'
storage_account_key = '<YOUR-STORAGE-KEY>'
storage_account_container = 'audioupload'
# 12_dec_1.1.9_English_001-AHO.mp3
# _3121512Dec_7mins_Sample.mp3
file_name = '_13121512_dec_1.1.4_English_001-AHO.mp3'
storage_account_url = f'https://{storage_account_name}.blob.core.windows.net/'
DOWNLOAD_AUDIO_SAS_TOKEN = "sp=rw&st=2022-11-03T06:14:12Z&se=2025-12-31T14:14:12Z&spr=https&sv=2021-06-08&sr=c&sig=zkvCpNBKqN08omZ9ZfRz9G34pYsf9Cpc%2BFXNxXLqfzE%3D"
BLOB_STORAGE_ACCOUNT_URL = "https://azcdsstoragefapp01d.blob.core.windows.net/"

STORAGE_ACCOUNT_NAME = "azcdsstoragefapp01d",
STORAGE_ACCOUNT_CONTAINER = "audioupload",
SAS_TOKEN_AUDIO_BOLB = "sp=r&st=2022-11-02T09:47:46Z&se=2025-12-31T17:47:46Z&spr=https&sv=2021-06-08&sr=c&sig=oeyh0YLTL4%2FjDNYsEwGxkkCx2YfKwY%2Bae%2F8OpNCDzX4%3D"
Speech_Key = 'e3bc96ab479246aca7fd9ee3bcc599ea'
speech_location = 'eastus'

translation_key = 'c991b604f7174fa88c2581ec8224bb91'

translation_location = 'eastus'
audio_to_text = None


# convert one language text to another language text
def GetTranslation(base_text, language_code):
    print("Start GetTranslation for", language_code)
    # print("Base Text",base_text)

    import requests
    import json

    translation_category = {
        'de': '8cb512ee-0889-4600-ad01-c44cf40ef694-TECH',
        'es': '8cb512ee-0889-4600-ad01-c44cf40ef694-TECH',
        'fr': '8cb512ee-0889-4600-ad01-c44cf40ef694-TECH',
        'pt': '8cb512ee-0889-4600-ad01-c44cf40ef694-TECH',
        'ko': '8cb512ee-0889-4600-ad01-c44cf40ef694-TECH',
        'it': '8cb512ee-0889-4600-ad01-c44cf40ef694-TECH',
        'ja': '8cb512ee-0889-4600-ad01-c44cf40ef694-TECH',
        'zh-Hans': '8cb512ee-0889-4600-ad01-c44cf40ef694-TECH',
        'ar': '8cb512ee-0889-4600-ad01-c44cf40ef694-TECH'
    }

    # url = 'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to={}&category={}'.format(language_code, os.environ.get('TRANSLATION_MODEL_CATEGORY'))
    url = 'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to={}&category={}'.format(
        language_code, translation_category[language_code])
    headers = {
        'Ocp-Apim-Subscription-Key': TRANSLATION_KEY,
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Region': 'eastus2'
    }
    body = [
        {
            "Text": base_text
        }
    ]
    print(body)
    r = requests.post(url=url, headers=headers, data=json.dumps(body))
    result = r.json()
    print("converted GetTranslation for", language_code, r.json())
    print("Finish GetTranslation for", language_code)
    if len(result) == 1:
        print(result)
        if len(result[0]['translations']) > 0:
            return (result[0]['translations'][0]['text'])
        else:
            return base_text
    else:
        return base_text


# Speech To Text
def GetSpeechToTextTranscription(storage_account_name, storage_account_container, filename, sas_token,
                                 speech_to_text_key, speech_service_location):
    print("Start GetSpeechToTextTranscription")
    import time
    import requests
    # Speech-to-text request structure. Details @ https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/batch-transcription-create?pivots=rest-api
    print(storage_account_name)
    print(storage_account_container)
    print(filename)
    print(sas_token)
    body = {
        "contentUrls": [
            f"https://azcdsstoragefapp01d.blob.core.windows.net/audioupload/{filename}?{SAS_TOKEN_AUDIO_BOLB}"
        ],
        "locale": "en-US",
        "displayName": f"{filename}_transcription",
        "properties": {
            "wordLevelTimestampsEnabled": True
        }
    }
    headers = {
        "Ocp-Apim-Subscription-Key": speech_to_text_key,
        "Content-Type": "application/json"
    }
    res = requests.post(
        url=f"https://{speech_service_location}.api.cognitive.microsoft.com/speechtotext/v3.0/transcriptions",
        data=json.dumps(body), headers=headers)

    # Check status of batch transcription job
    print("response", res.json())
    uri_2 = res.json()['self']
    uri_3 = None
    while True:
        res_2 = requests.get(uri_2, headers=headers)
        res_2_json = res_2.json()
        print(res_2_json['status'])
        if res_2_json['status'] == 'Succeeded' or res_2_json['status'] == 'Failed':
            uri_3 = res_2_json['links']['files']
            break
        else:
            time.sleep(2.5)

    # Get links to results
    res_3 = requests.get(uri_3, headers=headers)
    uri_4 = None
    for val in res_3.json()['values']:
        if val['kind'] == 'Transcription':
            print("url4", val['links']['contentUrl'])
            uri_4 = val['links']['contentUrl']

    # Retrieve combined recongized phrases
    res_4 = requests.get(uri_4, headers=headers)
    print("Finish GetSpeechToTextTranscription")
    return res_4.json()['combinedRecognizedPhrases'][0]['display']


# covert one audio to another audio language
def GetAudioTranslation(output_file, language_code, audio_text):
    # import ffmpeg
    language_voices = {'es': 'es-MX',
                       'fr': 'fr-FR',
                       'it': 'it-IT',
                       'de': 'de-DE',
                       'pt': 'pt-BR',
                       'ko': 'ko-KR',
                       'it': 'it-IT',
                       'ja': 'ja-JP',
                       'zh-Hans': 'zh-Hans',
                       }

    import azure.cognitiveservices.speech as speechsdk
    from azure.cognitiveservices.speech import AudioDataStream, SpeechConfig, SpeechSynthesizer, \
        SpeechSynthesisOutputFormat
    from azure.cognitiveservices.speech.audio import AudioOutputConfig

    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY,
                                           region=SPEECH_REGION)

    speech_result = audio_text
    print("speech result ", speech_result)
    translation = GetTranslation(speech_result, language_code)
    logging.info(f"speech result: {speech_result}")
    logging.info(f"translation: {translation}")
    audio_config = AudioOutputConfig(filename=output_file)

    raw_text_translation = translation

    translation = '<p>' + translation + '</p>'

    replacements = {
        'ecolab': '<phoneme alphabet="ipa" ph="iːk oʊ læb"> Ecolab </phoneme>',
        'Ecolab': '<phoneme alphabet="ipa" ph="iːk oʊ læb"> Ecolab </phoneme>',
        'eco lab': '<phoneme alphabet="ipa" ph="iːk oʊ læb"> Ecolab </phoneme>',
        'eco Lab': '<phoneme alphabet="ipa" ph="iːk oʊ læb"> Ecolab </phoneme>',
        'Eco Lab': '<phoneme alphabet="ipa" ph="iːk oʊ læb"> Ecolab </phoneme>',
        'trasar': '<phoneme alphabet="ipa" ph="ˈtreɪˈsɑr"> TRASAR </phoneme>',
        'TRASAR': '<phoneme alphabet="ipa" ph="ˈtreɪˈsɑr"> TRASAR </phoneme>'
    }

    raw_replacements = {
        'ecolab': 'Ecolab',
        'eco lab': 'Ecolab',
        'eco Lab': 'Ecolab',
        'Eco Lab': 'Ecolab',
        'Eco lab': 'Ecolab',
    }

    for k, v in replacements.items():
        if k in translation:
            translation = translation.replace(k, v)

    for k, v in raw_replacements.items():
        if k in raw_text_translation:
            raw_text_translation = raw_text_translation.replace(k, v)
    auto_detect_language = speechsdk.languageconfig.AutoDetectSourceLanguageConfig()
    speech_config.speech_synthesis_voice_name = "en-US-JennyMultilingualNeural"

    speech_config.set_speech_synthesis_output_format(
        SpeechSynthesisOutputFormat["Audio24Khz160KBitRateMonoMp3"])
    synthesizer = SpeechSynthesizer(
        speech_config=speech_config, auto_detect_source_language_config=auto_detect_language, audio_config=audio_config)
    # synthesizer.speak_ssml(
    #     '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US"><voice name="en-US-JennyMultilingualNeural"><lang xml:lang="{}">{}</lang></voice></speak>'.format(
    #         language_voices[language_code], translation))
    synthesizer.speak_text(raw_text_translation)

    #     try:
    #         os.remove(output_file)
    #     except Exception as e:
    #         pass

    # ffmpeg.input(wav_output_file_name).output(output_file).run()
    # os.remove(wav_input_file_name)
    # os.remove(wav_output_file_name)
    return raw_text_translation


# BLOBAUDIOUPLOAD
def audioLanguageTranslation(filename, mp3_filename, genr_txt_filename, language, audio_text, data):
    import random
    import string

    log = []

    def getRandomString(length):
        """Generate a random string"""
        str = string.ascii_lowercase
        return ''.join(random.choice(str) for i in range(length))

    output_file_name = f'{getRandomString(12)}.mp3'

    # blob_client = BlobClient(account_url=STORAGE_ACCOUNT_URL, container_name=trans_container,
    #                          blob_name=filename.replace('.mp3', mp3_filename), credential=SAS_TOKEN)

    translated_text = GetAudioTranslation(output_file_name, language, audio_text)

    translated_data = None
    with open(output_file_name, 'rb') as file:
        translated_data = file.read()

    data.append([filename.replace('.mp3', mp3_filename), translated_data, True])
    data.append([filename.replace('.mp3', genr_txt_filename), translated_text, True])
    # data.append([f"{filename}_log_{language}.txt", "\n".join(log), True])

    os.remove(output_file_name)


def main():
    import tempfile
    global audio_to_text
    #     logging.info(f"Python blob trigger function processed blob \n"
    #                  f"Name: {myblob.name}\n"
    #                  f"Blob Size: {myblob.length} bytes")
    # blob_client = BlobClient(account_url=UPLOAD_STORAGE_ACCOUNT_URL, credential=blob_sas, container_name='audioupload',
    #                          blob_name=file_name)
    # myblob = blob_client.download_blob()
    # Get temporary directory
    # tempdir = tempfile.gettempdir()
    # os.makedirs(tempdir, exist_ok=True)

    # Get uploaded file name
    filename = file_name.split('/')[-1]
    filename = filename.replace(' ', '_')
    logging.info(f"File Name: {filename}")

    if 'mp3' not in filename:
        return

    # Write blob data to temporary file
    # temp_path = os.path.join(tempdir, filename)
    # with open(temp_path, 'wb') as file:
    #     file.write(myblob.read())
    audio_to_text = GetSpeechToTextTranscription(storage_account_name=STORAGE_ACCOUNT_NAME,
                                                 storage_account_container=STORAGE_ACCOUNT_CONTAINER,
                                                 filename=file_name, sas_token=SAS_TOKEN_AUDIO_BOLB,
                                                 speech_to_text_key=SPEECH_KEY, speech_service_location=SPEECH_REGION)
    print(audio_to_text)
    from multiprocessing import Pool
    import multiprocessing as m

    p = Pool(m.cpu_count())
    translation_list = []
    data = m.Manager().list()
    # Spanish
    # audioLanguageTranslation(filename, '_AzTranslated-es.mp3', '_AzTranslated-es.txt', temp_path, output_path, 'es')
    translation_list.append([filename, '_AzTranslated-es.mp3', '_AzTranslated-es.txt', 'es', audio_to_text, data])

    # French
    # audioLanguageTranslation(filename, '_AzTranslated-fr.mp3', '_AzTranslated-fr.txt', temp_path, output_path, 'fr')
    translation_list.append([filename, '_AzTranslated-fr.mp3', '_AzTranslated-fr.txt', 'fr', audio_to_text, data])

    # German
    # audioLanguageTranslation(filename, '_AzTranslated-de.mp3', '_AzTranslated-de.txt', temp_path, output_path, 'de')
    translation_list.append([filename, '_AzTranslated-de.mp3', '_AzTranslated-de.txt', 'de', audio_to_text, data])

    # Portugese
    # audioLanguageTranslation(filename, '_AzTranslated-pt.mp3', '_AzTranslated-pt.txt', temp_path, output_path, 'pt')
    translation_list.append([filename, '_AzTranslated-pt.mp3', '_AzTranslated-pt.txt', 'pt', audio_to_text, data])

    # Korean
    # audioLanguageTranslation(filename, '_AzTranslated-ko.mp3', '_AzTranslated-ko.txt', temp_path, output_path, 'ko')
    translation_list.append([filename, '_AzTranslated-ko.mp3', '_AzTranslated-ko.txt', 'ko', audio_to_text, data])

    # Italian
    # audioLanguageTranslation(filename, '_AzTranslated-it.mp3', '_AzTranslated-it.txt', temp_path, output_path, 'it')
    translation_list.append([filename, '_AzTranslated-it.mp3', '_AzTranslated-it.txt', 'it', audio_to_text, data])

    # Japanese
    # audioLanguageTranslation(filename, '_AzTranslated-ja.mp3', '_AzTranslated-ja.txt', temp_path, output_path, 'ja')
    translation_list.append([filename, '_AzTranslated-ja.mp3', '_AzTranslated-ja.txt', 'ja', audio_to_text, data])

    # Chinese
    # audioLanguageTranslation(filename, '_AzTranslated-zh-Hans.mp3', '_AzTranslated-zh-Hans.txt', temp_path, output_path,
    #                          'zh-Hans')
    translation_list.append(
        [filename, '_AzTranslated-zh-Hans.mp3', '_AzTranslated-zh-Hans.txt', 'zh-Hans', audio_to_text, data])

    # Arabic
    # audioLanguageTranslation(filename, '_AzTranslated-ar.mp3', '_AzTranslated-ar.txt', temp_path, output_path, 'ar')
    translation_list.append([filename, '_AzTranslated-ar.mp3', '_AzTranslated-ar.txt', 'ar', audio_to_text, data])

    p.starmap(audioLanguageTranslation, translation_list)
    service = BlobServiceClient(account_url=BLOB_STORAGE_ACCOUNT_URL,
                                credential=DOWNLOAD_AUDIO_SAS_TOKEN)
    container_client = service.get_container_client('audiodownload')
    print("data length", len(data))
    count = 0
    for d in data:
        count += 1
        container_client.upload_blob(d[0], d[1], overwrite=d[2])


if __name__ == "__main__":
    main()
