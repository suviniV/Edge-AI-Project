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


if __name__ == '__main__':
    app.run()

