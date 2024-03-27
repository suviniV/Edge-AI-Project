from flask import Flask, render_template, request, url_for, redirect

import logging
import csv

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


@app.route('/ActiveUsers')
def ActiveUsers():
    users = []

    # Read user details from CSV file
    with open('Database/activeUsers.csv', 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            users.append(row)

    return render_template('ActiveUsers.html', users=users)


@app.route('/homepage')
def home():
    # Read the door status from the CSV file
    door_status = read_door_status_from_csv()

    # Pass the door status to the HTML template
    return render_template("homepage.html", door_status=door_status)



def read_door_status_from_csv():
    door_status = "locked"

    # with open('Database/doorstatus.csv', 'r') as file:
    #     reader = csv.reader(file)
    #
    #     for row in reader:
    #         door_status = row[0]
    #         break

    return door_status


@app.route('/user-management')
def user_management():
    return render_template("UserManagement.html")



@app.route('/AccessLogs')
def AccessLogs():
    logs = []

    # Read user details from CSV file
    with open('Database/accessLogs.csv', 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            logs.append(row)

    return render_template("AccessLogs.html", logs=logs)


@app.route('/UnauthorizedAccess')
def UnauthorizedAccess():
    UnauthorizedAccesslogs = []

    # Read user details from CSV file
    with open('Database/unathorizedAccess.csv', 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            UnauthorizedAccesslogs.append(row)

    return render_template("UnauthorizedAccess.html", UnauthorizedAccesslogs=UnauthorizedAccesslogs)


if __name__ == '__main__':
    app.run()

