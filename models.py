from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    industry = db.Column(db.String(50), nullable=False)

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
