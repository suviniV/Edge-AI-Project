from Model.functions import download_images_from_azure_storage, images_to_yml_and_training


def func():
    download_images_from_azure_storage('Model/trainingImages/2', "second")
    images_to_yml_and_training('trainingImages', 'trainingData.yml')
