# Ecolab_AI_Translations

This repository contains code for creating an Azure Function which automatically retrieves Audio & Excel files from Azure Blob Storage and translates the content into Spanish, German, French, and Portugese using custom Azure AI Translation Models.



## Creating Custom Translation Models



To get started with creating custom AI translation models which incorporate business-specific terminology follow [the instructions associated with the linked Quickstart](https://docs.microsoft.com/en-us/azure/cognitive-services/translator/custom-translator/v2-preview/quickstart).



More details about Azure's custom AI translation service [can be found here](https://docs.microsoft.com/en-us/azure/cognitive-services/translator/).



Following model training, custom AI translation models can be deployed and consumed via REST API. The Azure Function code contained in this repo make calls to an existing set of Ecolab-specific AI translation models and can facilitate translation of English text into Spanish, Portugese, French and German.



The files included within the `./TranslationFiles` directory can be used to train custom AI translation models.



## Deploying the Azure Function



The code in this repository is designed to be deployed to an Azure Function via a docker container - this is required as several Linux dependencies are installed within a custom Docker environment. Using the included `Dockerfile` we can build a new image, push to an Azure Container Registry, and then deploy to an Azure Function App. To build and push your image into an Azure Container Registry execute the following commands:




## azcdsaicontreg01d

az login --scope https://management.core.windows.net//.default

az acr login --name azcdsaicontreg01d

docker build --tag eclaitranslation/aitransazfuncimage:0.0.42 .

docker tag eclaitranslation/aitransazfuncimage:0.0.42 azcdsaicontreg01d.azurecr.io/aitransazfuncimage:0.0.42

docker push azcdsaicontreg01d.azurecr.io/aitransazfuncimage:0.0.42

```



<i>Note: update the name of the included Azure container registry above.</i>



To create an Azure function on Linux from a custom container, you can follow [the tutorial linked here](https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-function-linux-custom-image?msclkid=1cba9964a66f11ecad34548f1593a898&tabs=in-process%2Cbash%2Cazure-cli&pivots=programming-language-python). After creating an Azure function with either a premium plan, or a dedicated App Service plan, you can target the uploaded docker image from your specified container registry.



## Azure Function Environment Variables



This Azure function is designed to translate text and audio files uploaded into a blob storage account within containers named `textupload` and `audioupload`, respectively. In  both cases, files uploaded to these locations automatically trigger translation activities and German/French/Spanish/Portugese variants are created and added to `textdownload` and `audiodownload` directories.



The Azure Function expects the following variables to be present:



| Key                                 | Value                                    |

|-------------------------------------|------------------------------------------|

| AzureWebJobsStorage                 | The connection string to the storage account used by the Functions runtime.  To use the storage emulator, set the value to UseDevelopmentStorage=true |

| FUNCTIONS_WORKER_RUNTIME            | Set this value to `python` as this is a python Function App |

| STORAGE_ACCOUNT_URL | URL of the storage account which contains the containers `textupload`, `textdownload`, `audioupload`, and `audiodownload` where all English/Translated docs will be loaded. |

| SAS_TOKEN     | SAS token for accessing the containers in the storage account referenced above |

| TRANSLATION_KEY     | Key for the Azure Translation service |

| SPEECH_KEY     | Key for an Azure Speech Service - used to support audio translation |

| SPEECH_REGION     | Region where the Azure Speech Service is deployed |