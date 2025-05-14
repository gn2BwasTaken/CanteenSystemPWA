from flask import session, redirect, url_for, request, render_template, Flask
from functools import wraps
import models as dbHandler

app = Flask(__name__)

app.secret_key = 'BAD_SECRET_KEY'

def login_required(f): #run when websites are accessed that need security (e.g. home.html)
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def bypass_login_if_in_session(f): # this bypasses the need to log in again if the user is already logged in and on the homepage.
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function



@app.route('/login', methods=['POST', 'GET'])
def login():
        if request.method=='POST':
            username = request.form['username']
            password = request.form['password']
            dbHandler.insertUser(username, password)
            users = dbHandler.retrieveUsers()
            return render_template('index.html', users=users)
        else:
            return render_template('index.html')
        

@app.route('/home', methods=['POST', 'GET'])
@login_required
def home():
    print("jello!!")

@app.route('/logout') #enables log out
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')