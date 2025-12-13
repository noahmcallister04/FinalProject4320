from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask import request, flash
from flask import session, redirect, url_for
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

@app.route('/')
def index():
    """Main menu page"""
    return render_template('index.html')

@app.route('/reservation', methods=['GET', 'POST'])
def make_reservation():
    """Make a reservation page"""
    seating_chart = get_seating_chart()
    cost_matrix = get_cost_matrix()
    
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        seat_row = request.form.get('seat_row')
        seat_column = request.form.get('seat_column')
        
        # Validation
        if not first_name or not last_name:
            flash('First name and last name are required', 'error')
            return render_template('reservation.html', 
                                 seating_chart=seating_chart, 
                                 cost_matrix=cost_matrix)
        
        try:
            seat_row = int(seat_row)
            seat_column = int(seat_column)
        except (ValueError, TypeError):
            flash('Invalid seat selection', 'error')
            return render_template('reservation.html', 
                                 seating_chart=seating_chart, 
                                 cost_matrix=cost_matrix)
        
        # Check if seat is valid
        if not (0 <= seat_row < 12 and 0 <= seat_column < 4):
            flash('Invalid seat selection', 'error')
            return render_template('reservation.html', 
                                 seating_chart=seating_chart, 
                                 cost_matrix=cost_matrix)
        
        # Check if seat is available
        if not is_seat_available(seat_row, seat_column):
            flash('This seat is already reserved. Please choose another seat.', 'error')
            return render_template('reservation.html', 
                                 seating_chart=seating_chart, 
                                 cost_matrix=cost_matrix)
        
        # Create reservation
        passenger_name = f"{first_name} {last_name}"
        eticket_number = generate_eticket_number()
        
        new_reservation = Reservation(
            passengerName=passenger_name,
            seatRow=seat_row,
            seatColumn=seat_column,
            eTicketNumber=eticket_number
        )
        
        db.session.add(new_reservation)
        db.session.commit()
        
        # Show confirmation
        return render_template('confirmation.html', 
                             passenger_name=passenger_name,
                             seat_row=seat_row,
                             seat_column=seat_column,
                             eticket_number=eticket_number)
    
    return render_template('reservation.html', 
                         seating_chart=seating_chart, 
                         cost_matrix=cost_matrix)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page and dashboard combined"""
    # Check if already logged in
    if session.get('admin_logged_in'):
        # Show dashboard
        seating_chart = get_seating_chart()
        total_sales = calculate_total_sales()
        reservations = Reservation.query.all()
        
        return render_template('admin.html', 
                             logged_in=True,
                             seating_chart=seating_chart, 
                             total_sales=total_sales,
                             reservations=reservations)
    
    # Handle login attempt
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('You must enter a username', 'error')
            return render_template('admin.html', logged_in=False)
        
        admin = Admin.query.filter_by(username=username, password=password).first()
        
        if admin:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            
            # Show dashboard after successful login
            seating_chart = get_seating_chart()
            total_sales = calculate_total_sales()
            reservations = Reservation.query.all()
            
            return render_template('admin.html', 
                                 logged_in=True,
                                 seating_chart=seating_chart, 
                                 total_sales=total_sales,
                                 reservations=reservations)
        else:
            flash('Invalid credentials', 'error')
    
    # Show login form
    return render_template('admin.html', logged_in=False)

@app.route('/admin/logout')
def admin_logout():
    """Logout admin"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/admin/delete_reservation/<int:reservation_id>', methods=['POST'])
def delete_reservation(reservation_id):
    """Delete a reservation"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    reservation = Reservation.query.get_or_404(reservation_id)
    db.session.delete(reservation)
    db.session.commit()
    flash('Reservation deleted successfully', 'success')
    
    return redirect(url_for('admin_login'))
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
