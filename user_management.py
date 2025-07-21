import sqlite3 as sql
import time
import random
from models import UserCurrentCart, Purchases, User
from main import db

blacklist = [
    "=","-","'"
]

def insertUser(username, password, DoB, customerType):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO users (username,password,dateOfBirth,customerType) VALUES (?,?,?,?)",
        (username, password, DoB, customerType),
    )
    con.commit()
    con.close()


def retrieveUsers(username, password):
    for z in blacklist:
        if z in username:
            return False
        if z in password:
            return False
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM users WHERE username = '{username}'")
    if cur.fetchone() == None:
        con.close()
        return False
    else:
        cur.execute(f"SELECT * FROM users WHERE password = '{password}'")
        time.sleep(random.randint(80, 90) / 1000)
        if cur.fetchone() == None:
            con.close()
            return False
        else:
            con.close()
            return True


def insertFood(feedback):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(f"INSERT INTO feedback (feedback) VALUES ('{feedback}')")
    con.commit()
    con.close()

def InsertIntoCart(foodIdToAdd, user, additionalDesc):
    new_cart = UserCurrentCart(
        foodId=foodIdToAdd,
        userId=user,
        foodItemInstructions=additionalDesc
    )
    db.session.add(new_cart)
    db.session.commit()

def removeFromCart(food_id):
    deletion = UserCurrentCart.query.filter_by(cartId=food_id).delete()
    db.session.commit()

def buyCart(user_id):
    allCarts = UserCurrentCart.query.filter_by(userId=user_id)
    user = User.query.filter_by(id=user_id).first()
    
    for cart in allCarts:
        newPurchase = Purchases(
            foodId=cart.foodId,
            userId=cart.userId,
            Instructions=cart.foodItemInstructions,
            companyId=user.companyUnder
        )
        db.session.add(newPurchase)
    
    deletion = UserCurrentCart.query.filter_by(userId=user_id).delete()
    db.session.commit()

def listFood(companyId):
    con = sql.connect("instance/database.db")
    cur = con.cursor()
    data = cur.execute(f"SELECT * FROM food_item WHERE companyUnder ={companyId}").fetchall()
    con.close()
    f = open("templates/partials/all_food_items.html", "w")
    for row in data:
        f.write(f"<div class={"foodItemBox"}>\n")
        f.write(f"<img class={"foodImg"} src={row[4]}>\n")
        f.write(f"<p class={"foodName"}>{row[1]}</p>\n")
        f.write(f"<p class={"foodType"}>{row[2]}</p>\n")
        f.write(f"<p class={"foodDesc"}>{row[3]}</p>\n")
        f.write(f'<a href="items/{row[0]}" class="foodButton">View More</a>\n')
        f.write("</div>\n")
    f.close()
