from flask import Flask, session, request, redirect, url_for
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask import render_template

import user_management as dbHandler

# Code snippet for logging a message
# app.logger.critical("message")

app = Flask(__name__)

app.config['SECRET_KEY'] = b'2552f50a3f12626fcce85e0a09413e1b0a6ca6c69e64b1f7'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

Session(app)

with app.app_context():
    db.create_all()

def login_required(f): #run when websites are accessed that need security (e.g. home.html)
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


def bypass_login_if_in_session(f): # this bypasses the need to log in again if the user is already logged in and on the homepage.
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session:
            return redirect(url_for('systemPage'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/home.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@login_required
def systemPage():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        if 'username' in session: 
            feedback = request.form["feedback"]
            dbHandler.insertFeedback(feedback)
            dbHandler.listFeedback()
            return render_template("/home.html", state=True, value="Back")
    else:
        dbHandler.listFeedback()
        return render_template("/home.html", state=True, value="Back")


@app.route("/signup.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@bypass_login_if_in_session
def signup():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        if len(request.form["password"]) < 12:
            return redirect(url_for('home'))
        username = request.form["username"]
        password = generate_password_hash(request.form['password'])
        dateOfBirth = request.form["dob"]
        typeOfAccount = request.form["typeOfAccount"]
        new_user = User(username=username, password=password, dateOfBirth=dateOfBirth, customerType=typeOfAccount)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template("/signup.html")


@app.route("/index.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@app.route("/", methods=["POST", "GET"])
@bypass_login_if_in_session
def home():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['username'] = user.username
                return render_template("/home.html", value=username, state=True)
            else:
                return redirect(url_for('home'))
        except:
            return 'An error occured'

    else:
        return render_template("/index.html")

@app.route('/logout') #enables log out
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="0.0.0.0", port=5000)
