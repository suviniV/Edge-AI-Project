from Model.functions import download_images_from_azure_storage, save_training_images_to_yml


def func():
    download_images_from_azure_storage('Model/trainingImages/2', "second")
    save_training_images_to_yml('trainingImages', 'trainingData.yml')
