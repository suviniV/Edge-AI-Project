from flask import Flask, render_template, request, url_for, redirect, jsonify
import csv
from datetime import datetime, timedelta
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


# Function to write new users to cloud database
def write_users_to_csv(users):
    with open('Database/activeUsers.csv', 'w', newline='') as file:
        fieldnames = ['name', 'email']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users)


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


app = Flask(__name__, static_folder='static')


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


# @app.route('/deleteUser', methods=['POST'])
# def delete_user():
#     index = int(request.json['index']) - 1  # Adjust index to match Python list indexing
#     users = read_users_from_csv()
#
#     if 0 <= index < len(users):
#         deleted_user = users.pop(index)
#         write_users_to_csv(users)
#         return jsonify({'message': 'User deleted successfully', 'user': deleted_user})
#     else:
#         return jsonify({'error': 'Invalid user index'})


@app.route('/ActiveUsers')
def active_users():
    account_name = "databasecw"
    account_key = "tor4V06NY6XHesq2z9vAZ55l3IWWTv9JpL1KT9S4CahV+e2+b9eh4nMy+cZlnpc6EW1WsYHh489/+AStZimtVQ=="
    container_name = "activeuserspics"

    users = read_activeUsers()

    container_sas_token = generate_container_sas_token(account_name, container_name, account_key)

    for user in users:
        user_name = user["name"]
        user[ 'pic_url'] = f"https://{account_name}.blob.core.windows.net/{container_name}/{user_name}.png?{container_sas_token}"

    return render_template('ActiveUsers.html', users=users)


@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('full-name')
    email = request.form.get('email')

    # Validate form data
    if not name or not email:
        return jsonify({'error': 'All fields are required'})

    # Add user data to CSV file
    with open('Database/activeUsers.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, email])

    return jsonify({'success': 'User Successfully Added'})


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
        user['pic_url'] = f"https://{account_name}.blob.core.windows.net/{container_name}/{user_name}.png?{container_sas_token}"

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
        user['pic_url'] = f"https://{account_name}.blob.core.windows.net/{container_name}/{user_name}.png?{container_sas_token}"

    return render_template("UnauthorizedAccess.html", UnauthorizedAccesslogs=unauthorized_access_logs)


if __name__ == '__main__':
    app.run()
