from flask_sqlalchemy import SQLAlchemy
import random

db = SQLAlchemy()

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(150), nullable=False)
    ownerID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    uniqueID = db.Column(db.Integer, unique=True)

    def __repr__(self):
        return f'<Company {self.name}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    dateOfBirth = db.Column(db.String(40), unique=False, nullable=False)
    customerType = db.Column(db.String(20), unique=False, nullable=False)
    companyUnder = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    foodType = db.Column(db.String(40), unique=False, nullable=False)
    description = db.Column(db.String(150), unique=False, nullable=False)
    foodImage = db.Column(db.String(200),unique=False, nullable=True)
    price = db.Column(db.Integer, nullable=True)
    companyUnder = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)

    def __repr__(self):
        return f'<FoodItem {self.name}>'

class UserCurrentCart(db.Model):
    cartId = db.Column(db.Integer, primary_key=True)
    foodId = db.Column(db.Integer, db.ForeignKey('food_item.id'), nullable=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    foodItemInstructions = db.Column(db.String(150), unique=False, nullable=True)
    
    def __repr__(self):
        return f'<CurrentCart {self.cartId}>'