from flask import Flask, render_template, request, url_for, redirect, jsonify, session
import csv
import time
import io
import subprocess
from datetime import datetime, timedelta
from Model.functions import capturing_training_images
from azure.storage.blob import generate_container_sas, ContainerSasPermissions, BlobServiceClient


# Function to generate SAS token for the blob container in Azure
def generate_container_sas_token(account_name, container_name, account_key):
    sas_token = generate_container_sas(
        account_name=account_name,
        container_name=container_name,
        account_key=account_key,
        permission=ContainerSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    return sas_token


# Function to read door status from cloud database
def read_door_status():
    status = []

    blob_service_client = BlobServiceClient.from_connection_string(
        "DefaultEndpointsProtocol=https;AccountName=databasecw;AccountKey"
        "=tor4V06NY6XHesq2z9vAZ55l3IWWTv9JpL1KT9S4CahV+e2+b9eh4nMy+cZlnpc6EW1WsYHh489/+AStZimtVQ==;EndpointSuffix"
        "=core.windows.net")

    container_client = blob_service_client.get_container_client("doorlockstatus")
    blob_client = container_client.get_blob_client("doorStatus.csv")
    blob_data = blob_client.download_blob()
    csv_content = blob_data.content_as_text()

    reader = csv.DictReader(csv_content.splitlines())
    for row in reader:
        status.append(row)
    status = [{key.strip('\ufeff'): value for key, value in item.items()} for item in status]

    for status in status:
        door_status = status["status"]

    return door_status


# Function to read active users from cloud database
def read_activeUsers():
    users = []

    blob_service_client = BlobServiceClient.from_connection_string(
        "DefaultEndpointsProtocol=https;AccountName=databasecw;AccountKey"
        "=tor4V06NY6XHesq2z9vAZ55l3IWWTv9JpL1KT9S4CahV+e2+b9eh4nMy+cZlnpc6EW1WsYHh489/+AStZimtVQ==;EndpointSuffix"
        "=core.windows.net")

    container_client = blob_service_client.get_container_client("activeusersinfo")
    blob_client = container_client.get_blob_client("activeUsers.csv")
    blob_data = blob_client.download_blob()
    csv_content = blob_data.content_as_text()

    reader = csv.DictReader(csv_content.splitlines())
    for row in reader:
        users.append(row)

    return users


# Function to read access logs from cloud database
def read_access_logs():
    logs = []

    blob_service_client = BlobServiceClient.from_connection_string(
        "DefaultEndpointsProtocol=https;AccountName=databasecw;AccountKey"
        "=tor4V06NY6XHesq2z9vAZ55l3IWWTv9JpL1KT9S4CahV+e2+b9eh4nMy+cZlnpc6EW1WsYHh489/+AStZimtVQ==;EndpointSuffix"
        "=core.windows.net")

    container_client = blob_service_client.get_container_client("accesslogs")
    blob_client = container_client.get_blob_client("accessLogs.csv")
    blob_data = blob_client.download_blob()
    csv_content = blob_data.content_as_text()

    reader = csv.DictReader(csv_content.splitlines())
    for row in reader:
        logs.append(row)
    logs = [{key.strip('\ufeff'): value for key, value in item.items()} for item in logs]

    return logs


def read_unauthorized_access():
    unauthorized_access_logs = []

    blob_service_client = BlobServiceClient.from_connection_string(
        "DefaultEndpointsProtocol=https;AccountName=databasecw;AccountKey"
        "=tor4V06NY6XHesq2z9vAZ55l3IWWTv9JpL1KT9S4CahV+e2+b9eh4nMy+cZlnpc6EW1WsYHh489/+AStZimtVQ==;EndpointSuffix"
        "=core.windows.net")

    container_client = blob_service_client.get_container_client("unauthorizedaccesslogs")
    blob_client = container_client.get_blob_client("unauthorizedAccess.csv")
    blob_data = blob_client.download_blob()
    csv_content = blob_data.content_as_text()

    reader = csv.DictReader(csv_content.splitlines())
    for row in reader:
        unauthorized_access_logs.append(row)
    unauthorized_access_logs = [{key.strip('\ufeff'): value for key, value in item.items()} for item in
                                unauthorized_access_logs]

    return unauthorized_access_logs


# Function to write new users to the cloud database
def write_activeUsers(users):
    csv_content = io.StringIO()
    fieldnames = ['name', 'email']

    writer = csv.DictWriter(csv_content, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(users)

    blob_service_client = BlobServiceClient.from_connection_string(
        "DefaultEndpointsProtocol=https;AccountName=databasecw;AccountKey="
        "tor4V06NY6XHesq2z9vAZ55l3IWWTv9JpL1KT9S4CahV+e2+b9eh4nMy+cZlnpc6EW1WsYHh489/+AStZimtVQ==;EndpointSuffix="
        "core.windows.net")

    container_client = blob_service_client.get_container_client("activeusersinfo")
    blob_client = container_client.get_blob_client("activeUsers.csv")
    blob_client.upload_blob(csv_content.getvalue(), overwrite=True)


# Function to add new users to the cloud database
def add_user_to_database(name, email, profile_picture):
    # Retrieve existing users from CSV file
    users = read_activeUsers()

    # Add new user's data to the existing users list
    users.append({'name': name, 'email': email})

    # Write updated user data back to CSV file
    write_activeUsers(users)

    # Save user's profile picture
    blob_service_client = BlobServiceClient.from_connection_string(
        "DefaultEndpointsProtocol=https;AccountName=databasecw;AccountKey="
        "tor4V06NY6XHesq2z9vAZ55l3IWWTv9JpL1KT9S4CahV+e2+b9eh4nMy+cZlnpc6EW1WsYHh489/+AStZimtVQ==;EndpointSuffix="
        "core.windows.net")

    container_client = blob_service_client.get_container_client("activeuserspics")
    blob_client = container_client.get_blob_client(f"{name}.png")
    blob_client.upload_blob(profile_picture.read(), overwrite=True)


def delete_user(index):
    try:
        # Load CSV data from blob storage
        blob_service_client = BlobServiceClient.from_connection_string(
            "DefaultEndpointsProtocol=https;AccountName=databasecw;AccountKey="
            "tor4V06NY6XHesq2z9vAZ55l3IWWTv9JpL1KT9S4CahV+e2+b9eh4nMy+cZlnpc6EW1WsYHh489/+AStZimtVQ==;EndpointSuffix="
            "core.windows.net")
        container_client = blob_service_client.get_container_client("activeusersinfo")
        blob_client = container_client.get_blob_client("activeUsers.csv")
        blob_data = blob_client.download_blob().readall().decode('utf-8')

        # Convert CSV data to list of dictionaries
        users = []
        csv_reader = csv.DictReader(io.StringIO(blob_data))
        for row in csv_reader:
            users.append(row)

        # Remove user at the specified index
        user_to_delete = users.pop(index - 1)

        # Write updated CSV data back to blob storage
        csv_content = io.StringIO()
        fieldnames = ['name', 'email']
        writer = csv.DictWriter(csv_content, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users)
        blob_client.upload_blob(csv_content.getvalue(), overwrite=True)

        return {'success': f'User {user_to_delete["name"]} has been deleted.'}
    except Exception as e:
        return {'error': str(e)}


def upload_images_to_azure_storage(container_name):
    account_name = "smartlocktrainingimages"
    account_key = "kwpvrBsa5FRw9z95H4O2Ov0fyWQBgdig/S8+I4YZIY8iChizBeHvX0SS2C4wqbr6CpHR96uU7ypu+AStV7xGUg=="

    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net/",
                                            credential=account_key)

    # Get a container client
    container_client = blob_service_client.get_container_client(container_name)

    # Upload images to the container
    for i in range(300):
        blob_client = container_client.upload_blob(name=f"frame{i}.jpg", data=open(f"frame{i}.jpg", "rb"))


app = Flask(__name__, static_folder='static')


@app.route('/add_user', methods=['POST'])
def add_user_route():
    name = request.form.get('full-name')
    email = request.form.get('email')
    profile_picture = request.files.get('file')

    # Add user to the database and save picture to Azure Blob Storage
    add_user_to_database(name, email, profile_picture)
    time.sleep(30)
    return render_template('TrainingData.html')


@app.route('/deleteUser', methods=['POST'])
def delete_user_route():
    try:
        index = request.json.get('index')
        response = delete_user(index)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/')
def login():
    return render_template("login.html")


# Hardcoded credentials for demonstration purposes
VALID_USERNAME = 'lak'
VALID_PASSWORD = '2001'


@app.route('/signin', methods=['POST'])
def signin():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == VALID_USERNAME and password == VALID_PASSWORD:
        # Valid credentials, redirect to homepage
        return redirect(url_for('home'))
    else:
        # Invalid credentials, render login page with error message
        error_message = 'Invalid username or password. Please try again.'
        return render_template('login.html', error_message=error_message, show_popup=True)


@app.route('/CreateNewUser')
def CreateNewUser():
    return render_template("CreateNewUser.html")


@app.route('/TrainingData')
def training_data():
    account_name = "databasecw"
    account_key = "tor4V06NY6XHesq2z9vAZ55l3IWWTv9JpL1KT9S4CahV+e2+b9eh4nMy+cZlnpc6EW1WsYHh489/+AStZimtVQ=="
    container_pics_name = "activeuserspics"

    users = read_activeUsers()
    container_pics_token = generate_container_sas_token(account_name, container_pics_name, account_key)

    if users:
        latest_user = users[-1]  # Retrieve the last user
        user_name = latest_user["name"]
        pic_url = f"https://{account_name}.blob.core.windows.net/{container_pics_name}/{user_name}.png?{container_pics_token}"
        return render_template("TrainingData.html", pic_url=pic_url, user=latest_user)
    else:
        # Handle case when there are no users
        return render_template("TrainingData.html", pic_url=None, user=None)


# Set the secret key for the application
app.config['SECRET_KEY'] = '1c0f99d5e76ce48e1f400dd8b091c09ee08d0f605ad68c78'


@app.route('/start_capturing_images')
def start_capturing_images():
    # Call the capturing_training_images function directly
    capturing_training_images()

    # After capturing images, upload them to Azure Storage
    upload_images_to_azure_storage("second")

    # Set the capture success flag in the session
    session['capture_success'] = True

    # Return a response indicating success
    return jsonify({'success': True})


@app.route('/ActiveUsers')
def active_users():
    account_name = "databasecw"
    account_key = "tor4V06NY6XHesq2z9vAZ55l3IWWTv9JpL1KT9S4CahV+e2+b9eh4nMy+cZlnpc6EW1WsYHh489/+AStZimtVQ=="
    container_name = "activeuserspics"

    users = read_activeUsers()

    container_sas_token = generate_container_sas_token(account_name, container_name, account_key)

    for user in users:
        user_name = user["name"]
        user[
            'pic_url'] = f"https://{account_name}.blob.core.windows.net/{container_name}/{user_name}.png?{container_sas_token}"

    return render_template('ActiveUsers.html', users=users)


@app.route('/home')
def home():
    door_status = read_door_status()

    return render_template("homepage.html", door_status=door_status)


@app.route('/user-management')
def user_management():
    return render_template("UserManagement.html")


@app.route('/AccessLogs')
def AccessLogs():
    account_name = "databasecw"
    account_key = "tor4V06NY6XHesq2z9vAZ55l3IWWTv9JpL1KT9S4CahV+e2+b9eh4nMy+cZlnpc6EW1WsYHh489/+AStZimtVQ=="
    container_name = "activeuserspics"

    logs = read_access_logs()

    container_sas_token = generate_container_sas_token(account_name, container_name, account_key)

    for user in logs:
        user_name = user["name"]
        user[
            'pic_url'] = f"https://{account_name}.blob.core.windows.net/{container_name}/{user_name}.png?{container_sas_token}"

    return render_template("AccessLogs.html", logs=logs)


@app.route('/UnauthorizedAccess')
def UnauthorizedAccess():
    account_name = "databasecw"
    account_key = "tor4V06NY6XHesq2z9vAZ55l3IWWTv9JpL1KT9S4CahV+e2+b9eh4nMy+cZlnpc6EW1WsYHh489/+AStZimtVQ=="
    container_name = "unauthorizedaccesspics"

    container_sas_token = generate_container_sas_token(account_name, container_name, account_key)

    unauthorized_access_logs = read_unauthorized_access()

    for user in unauthorized_access_logs:
        user_name = user["id"]
        user[
            'pic_url'] = f"https://{account_name}.blob.core.windows.net/{container_name}/{user_name}.png?{container_sas_token}"

    return render_template("UnauthorizedAccess.html", UnauthorizedAccesslogs=unauthorized_access_logs)


if __name__ == '__main__':
    app.run()
