import logging

import azure.functions as func
import json
import os
import tempfile
import pandas as pd
import requests
from bs4 import BeautifulSoup
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

def TraverseTree(node, list):
    try:
        for child in node.children:
            TraverseTree(child, list)
    except:
        list.append(node.text)
        return

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
        'ar' : '8cb512ee-0889-4600-ad01-c44cf40ef694-TECH'
    }

    url = 'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to={}&category={}'.format(language_code, translation_category[language_code])
    headers = {
        'Ocp-Apim-Subscription-Key': os.environ.get('TRANSLATION_KEY'),
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
    if len(result)==1:
        try:
            if len(result[0]['translations'])>0:
                return (result[0]['translations'][0]['text'])
            else:
                return base_text
        except Exception as e:
            return base_text
    else:
        return base_text

def ConductTranslationWork(target_language, file_path):
     
    abbvs = {
        'es': 'spanish',
        'de': 'german',
        'it': 'italian',
        'fr': 'french',
        'pt': 'portugese',
        'ko': 'korean',
        'it': 'italian',
        'ja': 'japanese',
        'zh-Hans': 'chinese'
    }
    translation_dict = {}
    # table_service = TableService(account_name=os.environ.get('TRANSLATION_TABLE_NAME'), account_key=os.environ.get('TRANSLATION_TABLE_KEY'))
    # try:
    #     translated_entities = table_service.query_entities(abbvs[target_language])
    #     for ent in translated_entities:
    #         try:
    #             translation_dict[ent['Source'].lower()] = ent['Translation']
    #         except Exception as ex:
    #             pass
    # except Exception as ex:
    #     pass

    # logging.info("Translation records: " + str(len(translation_dict.keys())))
    logging.info('Here')
    xls = pd.ExcelFile(file_path)

    sheet_dict = {}

    for sheet in xls.sheet_names:

        df = pd.read_excel(file_path, engine='openpyxl', sheet_name=sheet)

        length = len(df)
        print(length)
        logging.info(sheet)
        logging.info(length)

        translated_entries = []
        machine_translations = []
        try:
            df = df.rename(columns={'Current Text': 'Current Text (en-US)'})
        except Exception:
            pass

        for idx, row in df.iterrows():
            if not pd.isnull(row['Current Text (en-US)']):
                #Get original text (may or may not be valid HTML) and replace line breaks with ## - this simplifies parsing
                original_text = row['Current Text (en-US)'].replace('<br />', '##')
                #Use beautiful soup to decode/parse tags
                soup = BeautifulSoup(original_text)
                #Grab original (decoded) text from beautifulsoup
                original_text = "".join([str(x) for x in soup.contents])
                #Use TraverseTree helper function to get text from tags into mylist array
                mylist = []
                TraverseTree(soup, mylist)
                machine_translation = True
                #Iterate over all entries in mylist
                for entry in mylist:
                    if '##' in entry:
                        #Split at ## chars, these represent line breaks which will be inserted back in later
                        subparts = entry.split('##')
                        for part in subparts:
                            if part in original_text:
                                #Translate 'part' and replace original text
                                if part.lower() in translation_dict.keys():
                                    translated_text = translation_dict[part.lower()]
                                    machine_translation = False
                                else:
                                    translated_text = GetTranslation(part, target_language)
                                original_text = original_text.replace(part, translated_text)
                    else:
                        if entry in original_text:
                            #Translate 'part' and replace original text
                            if entry.lower() in translation_dict.keys(): #Check the Ecolab translation dictionary first, if there is a matching entry use this 
                                translated_text = translation_dict[entry.lower()]
                                machine_translation = False
                            else:
                                translated_text = GetTranslation(entry, target_language)
                            original_text = original_text.replace(entry, translated_text)
                
                translated_entries.append(original_text.replace('##', '<br />'))
                machine_translations.append(str(machine_translation))        
            else:
                translated_entries.append('')
                machine_translations.append('')
        col_name = 'Translated Text ({})'.format(target_language)
        try:
            col_name = [x for x in df if x.startswith('Translated')][0]
            # df = df.drop([trans_col_name], axis=1)
        except Exception as e:
            pass
        # col_name = 'Translated Text ({})'.format(target_language)
        df[col_name] = translated_entries
        # df['Translated Text'] = translated_entries
        # df['Machine Translated'] = machine_translations
        sheet_dict[sheet] = df
        # return df
    return sheet_dict

def ExcelTranslation(tempdir, temp_path, filename, langauge_code, service, genr_excel_filename):
    translated_container = 'textdownload'
    language_df = ConductTranslationWork(langauge_code, temp_path)
    translated_path = "{}/{}".format(tempdir, filename.replace('.xls', '_AzTranslated.xls'))
    # New
    writer = pd.ExcelWriter(translated_path, engine='openpyxl')
    for sheet_name, sheet in language_df.items():
        sheet.to_excel(writer, sheet_name=sheet_name, index=False)
    writer.save()
    # spanish_df.to_excel(translated_path, index=False)
    translated_data = None
    with open(translated_path, 'rb') as file:
        translated_data = file.read()
    container_client = service.get_container_client(translated_container)
    container_client.upload_blob(filename.replace('.xls', genr_excel_filename), translated_data, overwrite=True)
    os.remove(translated_path)
    language_df = None

def main(myblob: func.InputStream):
    
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")

    #Get temporary directory
    tempdir = tempfile.gettempdir()
    os.makedirs(tempdir, exist_ok=True)

    #Get uploaded file name
    filename = myblob.name.split('/')[-1]
    filename  = filename.replace(' ', '_')
    logging.info(f"File Name: {filename}")

    if 'xls' not in filename:
        return

    #Write blob data to temporary file
    temp_path = os.path.join(tempdir, filename)
    with open(temp_path, 'wb') as file:
        file.write(myblob.read())

    #Get container client
    service = BlobServiceClient(account_url=os.environ.get('STORAGE_ACCOUNT_URL'), credential=os.environ.get('SAS_TOKEN'))

    output_path = temp_path.replace('.xls', '_Translated.xls')

    #Spanish translations
    ExcelTranslation(tempdir, temp_path, filename, 'es', service, '_AzTranslated-es.xls')

    #French translations
    ExcelTranslation(tempdir, temp_path, filename, 'fr', service, '_AzTranslated-fr.xls')

    #German translations
    ExcelTranslation(tempdir, temp_path, filename, 'de', service, '_AzTranslated-de.xls')

    #Portugese translations
    ExcelTranslation(tempdir, temp_path, filename, 'pt', service, '_AzTranslated-pt.xls')

    #Korean translations
    ExcelTranslation(tempdir, temp_path, filename, 'ko', service, '_AzTranslated-ko.xls')

    #Italian translations
    ExcelTranslation(tempdir, temp_path, filename, 'it', service, '_AzTranslated-it.xls')

    #Japanese translations
    ExcelTranslation(tempdir, temp_path, filename, 'ja', service, '_AzTranslated-ja.xls')

    #Chinese translations
    ExcelTranslation(tempdir, temp_path, filename, 'zh-Hans', service, '_AzTranslated-zh-Hans.xls')

    #Arabic translations
    ExcelTranslation(tempdir, temp_path, filename, 'ar', service, '_AzTranslated-ar.xls')


    os.remove(temp_path)
















#     #Spanish translations
#     translated_container = 'textdownload'
#     #blob_client = BlobClient(account_url=os.environ.get('STORAGE_ACCOUNT_URL'), container_name=translated_container, blob_name=filename.replace('.xls', '_AzTranslated-es.xls'), credential=os.environ.get('SAS_TOKEN'))
#     # if not blob_client.exists():
#     spanish_df = ConductTranslationWork('es', temp_path)
#     translated_path = "{}/{}".format(tempdir, filename.replace('.xls', '_AzTranslated.xls'))
#     # New
#     writer = pd.ExcelWriter(translated_path, engine='openpyxl')
#     for sheet_name, sheet in spanish_df.items():
#         sheet.to_excel(writer, sheet_name=sheet_name, index=False)
#     writer.save()
#     # spanish_df.to_excel(translated_path, index=False)
#     translated_data = None
#     with open(translated_path, 'rb') as file:
#         translated_data = file.read()
#     container_client = service.get_container_client(translated_container)
#     container_client.upload_blob(filename.replace('.xls', '_AzTranslated-es.xls'), translated_data, overwrite=True)
#     os.remove(translated_path)
#     spanish_df = None

#     #French translations
#     translated_container = 'textdownload'
#     # blob_client = BlobClient(account_url=os.environ.get('STORAGE_ACCOUNT_URL'), container_name=translated_container, blob_name=filename.replace('.xls', '_AzTranslated-fr.xls'), credential=os.environ.get('SAS_TOKEN'))
#     # if not blob_client.exists():
#     french_df = ConductTranslationWork('fr', temp_path)
#     translated_path = "{}/{}".format(tempdir, filename.replace('.xls', '_AzTranslated.xls'))
#     # New
#     writer = pd.ExcelWriter(translated_path, engine='openpyxl')
#     for sheet_name, sheet in french_df.items():
#         sheet.to_excel(writer, sheet_name=sheet_name, index=False)
#     writer.save()
#     # french_df.to_excel(translated_path, index=False)
#     translated_data = None
#     with open(translated_path, 'rb') as file:
#         translated_data = file.read()
#     container_client = service.get_container_client(translated_container)
#     container_client.upload_blob(filename.replace('.xls', '_AzTranslated-fr.xls'), translated_data, overwrite=True)
#     os.remove(translated_path)
#     french_df = None

#     #German translations
#     translated_container = 'textdownload'
#     #blob_client = BlobClient(account_url=os.environ.get('STORAGE_ACCOUNT_URL'), container_name=translated_container, blob_name=filename.replace('.xls', '_AzTranslated-de.xls'), credential=os.environ.get('SAS_TOKEN'))
#     #if not blob_client.exists():
#     german_df = ConductTranslationWork('de', temp_path)
#     translated_path = "{}/{}".format(tempdir, filename.replace('.xls', '_AzTranslated.xls'))
#     # New
#     writer = pd.ExcelWriter(translated_path, engine='openpyxl')
#     for sheet_name, sheet in german_df.items():
#         sheet.to_excel(writer, sheet_name=sheet_name, index=False)
#     writer.save()
#     # german_df.to_excel(translated_path, index=False)
#     translated_data = None
#     with open(translated_path, 'rb') as file:
#         translated_data = file.read()
#     container_client = service.get_container_client(translated_container)
#     container_client.upload_blob(filename.replace('.xls', '_AzTranslated-de.xls'), translated_data, overwrite=True)
#     os.remove(translated_path)
#     german_df = None

#     #Portugese translations
#     translated_container = 'textdownload'
#     #blob_client = BlobClient(account_url=os.environ.get('STORAGE_ACCOUNT_URL'), container_name=translated_container, blob_name=filename.replace('.xls', '_AzTranslated-pt.xls'), credential=os.environ.get('SAS_TOKEN'))
#     #if not blob_client.exists():
#     portugese_df = ConductTranslationWork('pt', temp_path)
#     translated_path = "{}/{}".format(tempdir, filename.replace('.xls', '_AzTranslated.xls'))
#     #portugese_df.to_excel(translated_path, index=False)
#     # New
#     writer = pd.ExcelWriter(translated_path, engine='openpyxl')
#     for sheet_name, sheet in portugese_df.items():
#         sheet.to_excel(writer, sheet_name=sheet_name, index=False)
#     writer.save()
#     translated_data = None
#     with open(translated_path, 'rb') as file:
#         translated_data = file.read()
#     container_client = service.get_container_client(translated_container)
#     container_client.upload_blob(filename.replace('.xls', '_AzTranslated-pt.xls'), translated_data, overwrite=True)
#     os.remove(translated_path)
#     portugese_df = None
    
#     #Korean translations
#     translated_container = 'textdownload'
#     #blob_client = BlobClient(account_url=os.environ.get('STORAGE_ACCOUNT_URL'), container_name=translated_container, blob_name=filename.replace('.xls', '_AzTranslated-pt.xls'), credential=os.environ.get('SAS_TOKEN'))
#     #if not blob_client.exists():
#     korean_df = ConductTranslationWork('ko', temp_path)
#     translated_path = "{}/{}".format(tempdir, filename.replace('.xls', '_AzTranslated.xls'))
#     #korean_df.to_excel(translated_path, index=False)
#     # New
#     writer = pd.ExcelWriter(translated_path, engine='openpyxl')
#     for sheet_name, sheet in korean_df.items():
#         sheet.to_excel(writer, sheet_name=sheet_name, index=False)
#     writer.save()
#     translated_data = None
#     with open(translated_path, 'rb') as file:
#         translated_data = file.read()
#     container_client = service.get_container_client(translated_container)
#     container_client.upload_blob(filename.replace('.xls', '_AzTranslated-ko.xls'), translated_data, overwrite=True)
#     os.remove(translated_path)
#     korean_df = None

#      #Italian translations
#     translated_container = 'textdownload'
#     #blob_client = BlobClient(account_url=os.environ.get('STORAGE_ACCOUNT_URL'), container_name=translated_container, blob_name=filename.replace('.xls', '_AzTranslated-pt.xls'), credential=os.environ.get('SAS_TOKEN'))
#     #if not blob_client.exists():
#     italian_df = ConductTranslationWork('it', temp_path)
#     translated_path = "{}/{}".format(tempdir, filename.replace('.xls', '_AzTranslated.xls'))
#     #italian.to_excel(translated_path, index=False)
#     # New
#     writer = pd.ExcelWriter(translated_path, engine='openpyxl')
#     for sheet_name, sheet in italian_df.items():
#         sheet.to_excel(writer, sheet_name=sheet_name, index=False)
#     writer.save()
#     translated_data = None
#     with open(translated_path, 'rb') as file:
#         translated_data = file.read()
#     container_client = service.get_container_client(translated_container)
#     container_client.upload_blob(filename.replace('.xls', '_AzTranslated-it.xls'), translated_data, overwrite=True)
#     os.remove(translated_path)
#     italian_df = None



#     #Japanese translations
#     translated_container = 'textdownload'
#     #blob_client = BlobClient(account_url=os.environ.get('STORAGE_ACCOUNT_URL'), container_name=translated_container, blob_name=filename.replace('.xls', '_AzTranslated-ja.xls'), credential=os.environ.get('SAS_TOKEN'))
#     #if not blob_client.exists():
#     japanese_df = ConductTranslationWork('ja', temp_path)
#     translated_path = "{}/{}".format(tempdir, filename.replace('.xls', '_AzTranslated.xls'))
#     #Japanese_df.to_excel(translated_path, index=False)
#     # New
#     writer = pd.ExcelWriter(translated_path, engine='openpyxl')
#     for sheet_name, sheet in japanese_df.items():
#         sheet.to_excel(writer, sheet_name=sheet_name, index=False)
#     writer.save()
#     translated_data = None
#     with open(translated_path, 'rb') as file:
#         translated_data = file.read()
#     container_client = service.get_container_client(translated_container)
#     container_client.upload_blob(filename.replace('.xls', '_AzTranslated-ja.xls'), translated_data, overwrite=True)
#     os.remove(translated_path)
#     japanese_df = None
    
#  #Chinese translations
#     translated_container = 'textdownload'
#     #blob_client = BlobClient(account_url=os.environ.get('STORAGE_ACCOUNT_URL'), container_name=translated_container, blob_name=filename.replace('.xls', '_AzTranslated-ch.xls'), credential=os.environ.get('SAS_TOKEN'))
#     #if not blob_client.exists():
#     chinese_df = ConductTranslationWork('zh-Hans', temp_path)
#     translated_path = "{}/{}".format(tempdir, filename.replace('.xls', '_AzTranslated.xls'))
#     #Chinese_df.to_excel(translated_path, index=False)
#     # New
#     writer = pd.ExcelWriter(translated_path, engine='openpyxl')
#     for sheet_name, sheet in chinese_df.items():
#         sheet.to_excel(writer, sheet_name=sheet_name, index=False)
#     writer.save()
#     translated_data = None
#     with open(translated_path, 'rb') as file:
#         translated_data = file.read()
#     container_client = service.get_container_client(translated_container)
#     container_client.upload_blob(filename.replace('.xls', '_AzTranslated-zh-Hans.xls'), translated_data, overwrite=True)
#     os.remove(translated_path)
#     chinese_df = None


#      #Arabic translations
#     translated_container = 'textdownload'
#     #blob_client = BlobClient(account_url=os.environ.get('STORAGE_ACCOUNT_URL'), container_name=translated_container, blob_name=filename.replace('.xls', '_AzTranslated-ch.xls'), credential=os.environ.get('SAS_TOKEN'))
#     #if not blob_client.exists():
#     arabic_df = ConductTranslationWork('ar', temp_path)
#     translated_path = "{}/{}".format(tempdir, filename.replace('.xls', '_AzTranslated.xls'))
#     #Arabic_df.to_excel(translated_path, index=False)
#     # New
#     writer = pd.ExcelWriter(translated_path, engine='openpyxl')
#     for sheet_name, sheet in arabic_df.items():
#         sheet.to_excel(writer, sheet_name=sheet_name, index=False)
#     writer.save()
#     translated_data = None
#     with open(translated_path, 'rb') as file:
#         translated_data = file.read()
#     container_client = service.get_container_client(translated_container)
#     container_client.upload_blob(filename.replace('.xls', '_AzTranslated-ar.xls'), translated_data, overwrite=True)
#     os.remove(translated_path)
#     arabic_df = None
    

    