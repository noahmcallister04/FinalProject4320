from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)