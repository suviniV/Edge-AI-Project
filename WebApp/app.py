from distributed.http.utils import redirect
from flask import Flask, render_template, request, url_for
import logging

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
        return render_template('homepage.html', error_message=None)
    else:
        # Invalid credentials, render login page with error message
        error_message = 'Invalid username or password. Please try again.'
        return render_template('login.html', error_message=error_message)

@app.route('/CreateNewUser')
def CreateNewUser():
    return render_template("CreateNewUser.html")


@app.route('/ActiveUsers')
def ActiveUsers():
    return render_template("ActiveUsers.html")


@app.route('/homepage')
def home():
    return render_template("homepage.html")


@app.route('/user-management')
def user_management():
    return render_template("UserManagement.html")


@app.route('/door-status')
def door_status():
    return render_template("door-status.html")


@app.route('/AccessLogs')
def AccessLogs():
    return render_template("AccessLogs.html")


@app.route('/UnauthorizedAccess')
def UnauthorizedAccess():
    return render_template("UnauthorizedAccess.html")


if __name__ == '__main__':
    app.run()

