# !pip install --upgrade azure-cognitiveservices-speech

from azure.storage.blob import BlobServiceClient, BlobClient
import os
import json
import logging
import azure.functions as func

audio_to_text = None


# convert one language text to another language text
def GetTranslation(base_text, language_code):
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
        'Ocp-Apim-Subscription-Key': os.environ.get("TRANSLATION_KEY"),
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Region': 'eastus2'
    }
    body = [
        {
            "Text": base_text
        }
    ]

    r = requests.post(url=url, headers=headers, data=json.dumps(body))
    result = r.json()
    if len(result) == 1:
        if len(result[0]['translations']) > 0:
            return (result[0]['translations'][0]['text'])
        else:
            return base_text
    else:
        return base_text


# Speech To Text
def GetSpeechToTextTranscription(filename, sas_token, speech_to_text_key, speech_service_location):
    import time
    import requests
    # Speech-to-text request structure. Details @ https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/batch-transcription-create?pivots=rest-api

    body = {
        "contentUrls": [
            f"https://azcdsstoragefapp01d.blob.core.windows.net/audioupload/{filename}?{sas_token}"
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
    uri_2 = res.json()['self']
    uri_3 = None
    while True:
        res_2 = requests.get(uri_2, headers=headers)
        res_2_json = res_2.json()
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
            uri_4 = val['links']['contentUrl']

    # Retrieve combined recongized phrases
    res_4 = requests.get(uri_4, headers=headers)
    return res_4.json()['combinedRecognizedPhrases'][0]['display']


# covert one audio to another audio language
def GetAudioTranslation(output_file, language_code, audio_text):
    # import ffmpeg
    import logging
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

    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get("SPEECH_KEY"),
                                           region=os.environ.get("SPEECH_REGION"))

    import random
    import string

    def getRandomString(length):
        """Generate a random string"""
        str = string.ascii_lowercase
        return ''.join(random.choice(str) for i in range(length))

    # wav_input_file_name = f'{getRandomString(12)}.wav'
    wav_output_file_name = f'{getRandomString(12)}.wav'

    # ffmpeg.input(source_file).output(wav_input_file_name).run()

    #     audio_input = speechsdk.AudioConfig(filename=wav_input_file_name)
    #     speech_recognizer = speechsdk.SpeechRecognizer(
    #         speech_config=speech_config, audio_config=audio_input)

    # speech_result = speech_recognizer.recognize_once_async().get()

    # speech_result = GetSpeechToTextTranscription(filename=upload_filename,
    #                                              sas_token=os.environ.get("UPLOAD_AUDIO_SAS_TOKEN"),
    #                                              speech_to_text_key=os.environ.get("SPEECH_KEY"),
    #                                              speech_service_location=os.environ.get("SPEECH_REGION"))
    speech_result = audio_text

    translation = GetTranslation(speech_result, language_code)
    logging.info(f"speech result: {speech_result}")
    logging.info(f"translation: {translation}")
    audio_config = AudioOutputConfig(filename=wav_output_file_name)

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
    import ffmpeg
    ffmpeg.input(wav_output_file_name).output(output_file).run()
    # os.remove(wav_input_file_name)
    os.remove(wav_output_file_name)
    return raw_text_translation


# BLOBAUDIOUPLOAD
def audioLanguageTranslation(filename, mp3_filename, genr_txt_filename, language, audio_text, data):
    import random
    import string
    try:
        def getRandomString(length):
            """Generate a random string"""
            str = string.ascii_lowercase
            return ''.join(random.choice(str) for i in range(length))

        output_file_name = f'{getRandomString(12)}.mp3'

        # blob_client = BlobClient(account_url=os.environ.get("STORAGE_ACCOUNT_URL"), container_name=trans_container,
        #                          blob_name=filename.replace('.mp3', mp3_filename),
        #                          credential=os.environ.get("SAS_TOKEN"))
        # if not blob_client.exists():

        translated_text = GetAudioTranslation(output_file_name, language, audio_text)
        translated_data = None
        with open(output_file_name, 'rb') as file:
            translated_data = file.read()
        data.append([filename.replace('.mp3', mp3_filename), translated_data, True])
        data.append([filename.replace('.mp3', genr_txt_filename), translated_text, True])
        os.remove(output_file_name)

    except Exception as e:
        raise e


def main(myblob: func.InputStream):
    global audio_to_text
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")

    # Get uploaded file name
    filename = myblob.name.split('/')[-1]
    filename = filename.replace(' ', '_')
    logging.info(f"File Name: {filename}")

    if 'mp3' not in filename:
        logging.info(f"File is not mp3 {filename}")
        return
    try:
        logging.info(f"Start with audio translation for {filename}")
        audio_to_text = GetSpeechToTextTranscription(filename=filename,
                                                     sas_token=os.environ.get("UPLOAD_AUDIO_SAS_TOKEN"),
                                                     speech_to_text_key=os.environ.get("SPEECH_KEY"),
                                                     speech_service_location=os.environ.get("SPEECH_REGION"))
        logging.info(f"{audio_to_text}")
        service = BlobServiceClient(account_url=os.environ.get("STORAGE_ACCOUNT_URL"),
                                    credential=os.environ.get("SAS_TOKEN"))

        container_client = service.get_container_client('audiodownload')
        container_client.upload_blob(filename.replace('.mp3', '_AzTranslated.txt'), audio_to_text, overwrite=True)
        logging.info(f"uploaded translated text file for {filename}")
    except Exception as e:
        logging.info(f"For {filename} Exception {e}")
        raise e

    from multiprocessing import Pool
    import multiprocessing as m
    cores = 1 if m.cpu_count() == 1 else m.cpu_count() - 1

    logging.info(f"total cpu cores for this instance {cores}")

    p = Pool(cores)
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
    try:
        logging.info(f"started with multiprocessing for {filename}")
        p.starmap(audioLanguageTranslation, translation_list)
        for d in data:
            container_client.upload_blob(d[0], d[1], overwrite=d[2])
    except Exception as e:
        logging.info(f"For {filename} Exception {e}")
        raise e
    logging.info(f"finish with file {filename}")
    # os.remove(temp_path)
