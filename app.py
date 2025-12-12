from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets
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

# Cost Matrix Function
def get_cost_matrix():
    '''
    Function to generate cost matrix for flights
    Input: none
    Output: Returns a 12 x 4 matrix of prices
    '''
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    return cost_matrix

# Helper Functions
def get_seating_chart():
    """
    Creates a seating chart with reservation status
    Returns a 12x4 matrix with 'X' for reserved seats and 'O' for available seats
    """
    reservations = Reservation.query.all()
    chart = [['O' for col in range(4)] for row in range(12)]
    
    for reservation in reservations:
        row = reservation.seatRow
        col = reservation.seatColumn
        if 0 <= row < 12 and 0 <= col < 4:
            chart[row][col] = 'X'
    
    return chart

def is_seat_available(row, col):
    """
    Check if a seat is available
    """
    reservation = Reservation.query.filter_by(seatRow=row, seatColumn=col).first()
    return reservation is None

def init_db():
    """Initialize the database with tables"""
    with app.app_context():
        print(f"Initializing database at: {database_path}")
        db.create_all()
        print("Database tables created/verified")
        
        # Add a default admin if none exists
        try:
            admin_count = Admin.query.count()
            if admin_count == 0:
                default_admin = Admin(username='admin', password='admin123')
                db.session.add(default_admin)
                db.session.commit()
                print("Default admin created (username: admin, password: admin123)")
            else:
                print(f"Found {admin_count} admin account(s) in database")
        except Exception as e:
            print(f"Note: {e}")

def calculate_total_sales():
    """
    Calculate total sales based on all reservations
    """
    reservations = Reservation.query.all()
    cost_matrix = get_cost_matrix()
    total = 0
    
    for reservation in reservations:
        row = reservation.seatRow
        col = reservation.seatColumn
        if 0 <= row < 12 and 0 <= col < 4:
            total += cost_matrix[row][col]
    
    return total

def generate_eticket_number():
    """
    Generate a unique e-ticket number
    """
    return secrets.token_hex(6).upper()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)