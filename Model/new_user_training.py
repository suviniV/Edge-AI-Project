from functions import images_to_yml_and_training, download_images_from_azure_storage

download_images_from_azure_storage('trainingImages/2', "second")
images_to_yml_and_training('trainingImages', 'trainingData.yml')