from flask import Flask, render_template
import logging

app = Flask(__name__, static_folder='static')


@app.route('/')
def login():
    return render_template("login.html")


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

