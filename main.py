import logging
from logging.config import dictConfig
from flask import Flask, session, request, redirect, url_for
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Company, FoodItem, UserCurrentCart, Purchases
from emailSend import send_basic_message
from flask_session import Session
import random

#from sqlalchemy.orm import sessionmaker
#from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
import os
from PIL import Image

import user_management as dbHandler
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

def compress_image(input_path, output_path, quality=70):
    img = Image.open(input_path)
    img.save(output_path, optimize=True, quality=quality)


# Code snippet for logging a message
# app.logger.critical("message")

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#engine = create_engine('sqlite:///database.db')
#Session = sessionmaker(bind=engine)
#session = Session()

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
            #app.logger.info('in company: %s',  session['isInCompany'])
            app.logger.info('in company: %s',  session['isInCompany'])
            if session['isInCompany'] == 'No':
                return redirect(url_for('linkCompany'))
            else:
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
            dbHandler.insertFood(feedback)
            user1 = User.query.filter_by(username=session['username']).first()
            dbHandler.listFood(user1.companyUnder)
            count = UserCurrentCart.query.filter_by(userId=user1.id).count()
            return render_template("/home.html", state=True, value="Back", cartCount=count)
    else:
        user1 = User.query.filter_by(username=session['username']).first()
        count = UserCurrentCart.query.filter_by(userId=user1.id).count()
        dbHandler.listFood(user1.companyUnder)
        isManage = False
        if user1.customerType == "Employee":
            isManage = True
        return render_template("/home.html", state=True, value="Back", cartCount=count, isManaging=isManage)
    
@app.route("/linkCompany.html", methods=["POST", "GET"])
@login_required
def linkCompany():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        if 'username' in session: 
            compNumber = int(request.form["compNumber"])
            comp = Company.query.filter_by(uniqueID=compNumber).first()
            if comp:
                app.logger.info("your company number is: " + str(compNumber))
                db.session.query(User).filter_by(username=session['username']).update({'companyUnder': comp.id})
                db.session.commit()
                if comp.ownerID == None:
                    app.logger.info("will change now! make sure to do it!")
                session['isInCompany'] = 'Yes'
                return render_template("/home.html", state=True, value="Back")
            else:
                return render_template("/linkCompany.html", state=True, value="Back")
    else:
        isanEmployee = False
        if session['customerType'] == 'Employee':
            isanEmployee = True
        return render_template("/linkCompany.html", state=True, value='Back', IsEmployee=isanEmployee)

@app.route("/createCompany.html", methods=["POST", "GET"]) 
@login_required
def createCompany():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        if 'username' in session: 
            app.logger.info(session['username'])
            user = User.query.filter_by(username=session['username']).first()
            app.logger.info(user.id)
            nameOfCompany = request.form["nameOfCompany"]
            randy1 = random.randint(100000,999999)
            new_company = Company(name=nameOfCompany, description="add a description", ownerID=user.id, uniqueID=randy1)
            db.session.add(new_company)
            #doing user stuff now
            user1 = db.session.query(User).filter_by(id=user.id).first()
            user1.companyUnder = new_company.id
            db.session.commit()
            session['isInCompany'] = 'Yes'
            return redirect(url_for('home'))
    else:
        return render_template("/createCompany.html", state=True, value="Back")


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
                session['customerType'] = user.customerType
                app.logger.info(user.companyUnder)
                if user.companyUnder == None:
                    session['isInCompany'] = 'No'
                    return redirect(url_for('linkCompany'))
                else:
                    session['isInCompany'] = 'Yes'
                    return url_for('systemPage')
            else:
                return redirect(url_for('home'))
        except:
            return 'An error occured'

    else:
        return render_template("/index.html")

@app.route('/items/<item_id>')
def view_item(item_id):
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        item1 = db.session.query(FoodItem).filter_by(id=item_id).first()
        count = UserCurrentCart.query.filter_by(userId=user.id).count()
        if item1:
            if user.customerType == "Employee":
                employeeStats = True
            else:
                employeeStats = False
            FoodOptions = item1.foodOptions.split(",")
            return render_template("/item_viewer.html", itemName=item1.name, itemDesc=item1.description, itemImg=(item1.foodImage).replace("static/",""), state=True, itemId=item1.id, cartCount=count, options=FoodOptions, isEmployee=employeeStats)
        else:
            return "item not found"

@app.route('/manageFoodItem/<item_id>')
def manageFoodItem(item_id):
    if request.method == "POST":
        if 'username' in session:
            #insert the shit here
            return redirect(url_for('home'))
    else:
        food = FoodItem.query.filter_by(id=item_id).first()
        return render_template("/manageFoodItem.html", itemId=item_id, foodName=food.name, foodType=food.foodType, foodDescription=food.description, foodOptions=food.foodOptions, foodPrice=food.price, foodImage=(food.foodImage).replace("static/",""))

@app.route('/manageFoodItemActual', methods=["POST"])
def manageItem():
    return 0

@app.route('/notifyAboutPurchase/<purchase_id>')
def notifyAboutPurchase(purchase_id):
    purchase1 = Purchases.query.filter_by(purchaseId=purchase_id).first()
    food1 = FoodItem.query.filter_by(id=purchase1.foodId).first()
    userMail = "shadowgod266@outlook.com"
    send_basic_message(userMail,"Your purchase is available for pick up!",f'The food item: {food1.name} is now available for pick up! Please come to the counter.')
    return url_for('systemPage')

@app.route('/logout') #enables log out
def logout():
    session.pop('username', None) #removes session
    return redirect(url_for('home'))

@app.route('/manageCompany') #allows to manage company
@login_required
def manageCompany():
    user = User.query.filter_by(username=session['username']).first()
    company = Company.query.filter_by(id=user.companyUnder).first()
    owner = User.query.filter_by(id=company.ownerID).first()
    return render_template("manageCompany.html", companyName=company.name, companyOwner=owner.username, username=user.username, state=True)

@app.route('/addToCart/<food_id>', methods=["POST"]) #can add to cart
def addToCart(food_id):
    if request.method == "POST":
        if 'username' in session:
            options = ""
            options = request.form["typeOfFood"]
            user = User.query.filter_by(username=session['username']).first()
            dbHandler.InsertIntoCart(food_id,user.id,options)
            return redirect(url_for('home'))

@app.route('/removeFromCart/<food_id>') #removes an item from the cart!
def removeFromCart(food_id):
    if 'username' in session:
        app.logger.info(f'trying to delete: {food_id}')
        user = User.query.filter_by(username=session['username']).first()
        dbHandler.removeFromCart(food_id)
        return redirect(url_for('cartViewer'))

@app.route("/buyCart", methods=["POST","GET"])
def buyCart():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        cartsAll = UserCurrentCart.query.filter_by(userId=user.id).all()
        price = 0
        for cart in cartsAll:
            price += cart.food.price
        app.logger.info(price)
        dbHandler.buyCart(user.id)
        return redirect(url_for('home'))

@app.route("/cart", methods=["POST","GET"])
def cartViewer():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        cartsAll = UserCurrentCart.query.filter_by(userId=user.id).all()
        return render_template("/cart_viewer.html", carts=cartsAll)


@app.route("/allPurchases")
def allPurchases():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user.customerType == "Supplier" or user.customerType == "Employee":
            allPurchases = Purchases.query.filter_by(companyId=user.companyUnder).all()
            app.logger.info(allPurchases)
            return render_template("/allPurchases.html", purchases=allPurchases)
        else:
            return "your account type is not able to access this page"
    else:
        return "please log in"

@app.route('/addFoodItem', methods=["POST","GET"]) #enables food stuff
def addFoodItem():
    if request.method == "POST" and 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        image = request.files['image']
        filename = secure_filename(image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        image.save(filepath)

        compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"compressed_{filename}")
        img = Image.open(filepath)
        img.thumbnail((700,700))
        img.save(compressed_path.replace('.jpg','.webp'), optimize=True, quality=45, format='WEBP')
        new_item = FoodItem(
            name=request.form['nameOfFood'],
            foodType=request.form['typeOfFood'],
            description=request.form['descriptionText'],
            foodImage=compressed_path.replace(".jpg", ".webp"),
            price=request.form['foodPrice'],
            companyUnder=user.companyUnder,
            foodOptions=request.form['foodOptions']
        )
        db.session.add(new_item)
        db.session.commit()
        return render_template("/addFoodItem.html",state=True)
    else:
        return render_template("/addFoodItem.html",state=True)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.route('/viewUniqueCode')
@login_required
def viewUniqueCode():
    user = User.query.filter_by(username=session['username']).first()
    company = Company.query.filter_by(id=user.companyUnder).first()
    app.logger.info(user.companyUnder)
    return render_template("viewUniqueCode.html", companyCode=company.uniqueID)

if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="0.0.0.0", port=5000)