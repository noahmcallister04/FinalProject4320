from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'

# Get the directory where app.py is located
basedir = os.path.abspath(os.path.dirname(__file__))

# Database file should be in the same directory as app.py
database_path = os.path.join(basedir, 'reservations.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    passengerName = db.Column(db.Text, nullable=False)
    seatRow = db.Column(db.Integer, nullable=False)
    seatColumn = db.Column(db.Integer, nullable=False)
    eTicketNumber = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Admin(db.Model):
    __tablename__ = 'admins'
    username = db.Column(db.Text, primary_key=True)
    password = db.Column(db.Text, nullable=False)

if __name__ == '__main__':
    app.run(debug=True, port=5000)