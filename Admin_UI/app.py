from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime, timedelta
from app.chart_generator import ChartGenerator
from sqlalchemy import func, and_, or_
import math
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.jinja_env.globals.update(timedelta=timedelta)

class MomentHelper:
    @staticmethod
    def utcnow():
        return datetime.utcnow()

# Add helpers to Jinja globals
app.jinja_env.globals.update(
    timedelta=timedelta,
    moment=MomentHelper()
)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Helper Functions 
def init_database():
    """Initialize database with default admin"""
    with app.app_context():
        db.create_all()
        
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin_user = User(
                username='admin',
                password=generate_password_hash('admin123'),
                email='admin@parking.com',
                phone='1234567890',
                full_name='System Administrator',
                address='Admin Office',
                pin_code='000000',
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Database initialized with default admin!")

def create_parking_spots(lot_id, max_spots):
    """Create parking spots for a lot"""
    for i in range(1, max_spots + 1):
        spot = ParkingSpot(
            lot_id=lot_id,
            spot_number=f"A{i:03d}",  # A001, A002, etc.
            status='A'
        )
        db.session.add(spot)

def search_parking_lots(query):
    """Search parking lots by name, location, or pincode"""
    if not query:
        return ParkingLot.query.all()
    
    return ParkingLot.query.filter(
        or_(
            ParkingLot.prime_location_name.contains(query),
            ParkingLot.address.contains(query),
            ParkingLot.pin_code.contains(query)
        )
    ).all()

def search_users(query):
    """Search users by various fields"""
    if not query:
        return User.query.filter_by(is_admin=False).all()
    
    return User.query.filter(
        and_(
            User.is_admin == False,
            or_(
                User.username.contains(query),
                User.full_name.contains(query),
                User.email.contains(query),
                User.address.contains(query),
                User.pin_code.contains(query),
                User.phone.contains(query)
            )
        )
    ).all()

# ═══════════════════════════════════════════════════════════════
# AUTHENTICATION ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Validation
        username = request.form['username']
        email = request.form['email']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'error')
            return render_template('register.html')
        
        # Create new user
        new_user = User(
            username=username,
            password=generate_password_hash(request.form['password']),
            email=email,
            phone=request.form['phone'],
            full_name=request.form['full_name'],
            address=request.form['address'],
            pin_code=request.form['pin_code'],
            is_admin=False
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ═══════════════════════════════════════════════════════════════
# USER ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    # Search functionality
    search_query = request.args.get('search', '')
    lots = search_parking_lots(search_query)
    
    # User's active reservation
    active_reservation = Reservation.query.filter_by(
        user_id=current_user.id, 
        is_active=True
    ).first()
    
    # User's parking history
    parking_history = Reservation.query.filter_by(
        user_id=current_user.id
    ).order_by(Reservation.parking_timestamp.desc()).limit(10).all()
    
    return render_template('user_dashboard.html',
                         lots=lots,
                         active_reservation=active_reservation,
                         parking_history=parking_history,
                         search_query=search_query)

@app.route('/user_summary')
@login_required
def user_summary():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    # Get user's completed reservations
    completed_reservations = [r for r in current_user.reservations if not r.is_active]
    
    # Calculate location bookings using Python
    location_counts = {}
    for reservation in completed_reservations:
        location = reservation.spot.lot.prime_location_name
        location_counts[location] = location_counts.get(location, 0) + 1
    
    # Convert to list of tuples for chart
    location_bookings = [(location, count) for location, count in location_counts.items()]
    
    # Get duration data
    duration_data = []
    for reservation in completed_reservations:
        if reservation.leaving_timestamp:
            duration = reservation.leaving_timestamp - reservation.parking_timestamp
            hours = duration.total_seconds() / 3600
            duration_data.append({
                'date': reservation.parking_timestamp.strftime('%Y-%m-%d'),
                'hours': round(hours, 2),
                'location': reservation.spot.lot.prime_location_name
            })
    
    # Sort by date
    duration_data.sort(key=lambda x: x['date'])
    
    # Generate charts using matplotlib
    location_chart_url = ChartGenerator.generate_user_location_chart(location_bookings)
    duration_chart_url = ChartGenerator.generate_user_duration_chart(duration_data)
    
    return render_template('user_summary.html',
                         location_chart_url=location_chart_url,
                         duration_chart_url=duration_chart_url,
                         location_bookings=location_bookings,
                         duration_data=duration_data)



@app.route('/book_confirmation/<int:lot_id>')
@login_required
def book_confirmation(lot_id):
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    
    # Check for active reservation
    if Reservation.query.filter_by(user_id=current_user.id, is_active=True).first():
        flash('You already have an active parking reservation!', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Find available spot
    available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
    if not available_spot:
        flash('No available spots in this parking lot!', 'error')
        return redirect(url_for('user_dashboard'))
    
    return render_template('book_confirmation.html', 
                         lot=lot, 
                         spot=available_spot,
                         user=current_user)

@app.route('/confirm_booking', methods=['POST'])
@login_required
def confirm_booking():
    spot_id = request.form['spot_id']
    vehicle_license_plate = request.form['vehicle_license_plate']
    vehicle_color = request.form['vehicle_color']
    
    spot = ParkingSpot.query.get_or_404(spot_id)
    
    if spot.status != 'A':
        flash('Spot no longer available!', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Create reservation
    reservation = Reservation(
        spot_id=spot_id,
        user_id=current_user.id,
        vehicle_license_plate=vehicle_license_plate,
        vehicle_color=vehicle_color,
        parking_timestamp=datetime.utcnow(),
        is_active=True
    )
    
    # Update spot status
    spot.status = 'O'
    
    db.session.add(reservation)
    db.session.commit()
    
    flash(f'Parking spot {spot.spot_number} booked successfully!', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/release_confirmation/<int:reservation_id>')
@login_required
def release_confirmation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    if reservation.user_id != current_user.id:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Calculate cost
    current_time = datetime.utcnow()  # Get current UTC time
    duration = current_time - reservation.parking_timestamp
    hours = duration.total_seconds() / 3600
    charged_hours = max(1, math.ceil(hours))
    cost = charged_hours * reservation.spot.lot.price
    
    return render_template('release_confirmation.html',
                         reservation=reservation,
                         duration_hours=round(hours, 2),
                         charged_hours=charged_hours,
                         total_cost=round(cost, 2),
                         current_time=current_time)  


@app.route('/confirm_release', methods=['POST'])
@login_required
def confirm_release():
    reservation_id = request.form['reservation_id']
    reservation = Reservation.query.get_or_404(reservation_id)
    
    if reservation.user_id != current_user.id:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Debug: Print before update
    print(f"Before release - User spending: {current_user.get_total_spending()}")
    print(f"Before release - Reservation cost: {reservation.parking_cost}")
    
    # Set leaving timestamp first
    reservation.leaving_timestamp = datetime.utcnow()
    
    # Calculate and update cost using the model method
    cost, hours = reservation.calculate_cost(reservation.spot.lot.price)
    reservation.parking_cost = cost
    reservation.hours_charged = hours
    reservation.is_active = False
    
    # Update spot status
    reservation.spot.status = 'A'
    
    # Commit changes to database
    db.session.commit()
    
    # Debug: Print after update
    print(f"After release - User spending: {current_user.get_total_spending()}")
    print(f"After release - Reservation cost: {reservation.parking_cost}")
    print(f"After release - Cost calculated: {cost}")
    
    flash(f'Parking released! Total cost: ₹{cost} for {hours} hour(s)', 'success')
    return redirect(url_for('user_dashboard'))

# ═══════════════════════════════════════════════════════════════
# ADMIN ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    # Search functionality
    search_query = request.args.get('search', '')
    lots = search_parking_lots(search_query)
    
    return render_template('admin_dashboard.html', 
                         lots=lots, 
                         search_query=search_query)

@app.route('/admin_users')
@login_required
def admin_users():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    # Search functionality
    search_query = request.args.get('search', '')
    users = search_users(search_query)
    
    return render_template('admin_users.html', 
                         users=users, 
                         search_query=search_query)

@app.route('/admin_summary')
@login_required
def admin_summary():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    # Daily occupancy data (last 30 days)
    days_back = 30
    occupancy_data = []
    
    for i in range(days_back):
        date = datetime.utcnow().date() - timedelta(days=i)
        
        lots_data = []
        for lot in ParkingLot.query.all():
            occupied_count = 0
            
            for reservation in Reservation.query.filter(
                Reservation.spot_id.in_([s.id for s in lot.spots])
            ).all():
                start_date = reservation.parking_timestamp.date()
                end_date = reservation.leaving_timestamp.date() if reservation.leaving_timestamp else datetime.utcnow().date()
                
                if start_date <= date <= end_date:
                    occupied_count += 1
            
            lots_data.append({
                'name': lot.prime_location_name,
                'occupied': occupied_count,
                'total': lot.maximum_number_of_spots
            })
        
        occupancy_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'lots': lots_data
        })
    
    # Daily revenue data (last 30 days)
    revenue_data = []
    for i in range(days_back):
        date = datetime.utcnow().date() - timedelta(days=i)
        
        lots_revenue = []
        for lot in ParkingLot.query.all():
            daily_revenue = db.session.query(func.sum(Reservation.parking_cost)).filter(
                Reservation.spot_id.in_([s.id for s in lot.spots]),
                func.date(Reservation.leaving_timestamp) == date,
                Reservation.parking_cost.isnot(None),
                Reservation.is_active == False
            ).scalar() or 0
            
            lots_revenue.append({
                'name': lot.prime_location_name,
                'revenue': round(daily_revenue, 2)
            })
        
        revenue_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'lots': lots_revenue
        })
    
    # Generate charts using matplotlib
    lot_names = list(set([lot.prime_location_name for lot in ParkingLot.query.all()]))
    
    occupancy_chart_url = ChartGenerator.generate_occupancy_chart(
        list(reversed(occupancy_data)), lot_names
    )
    revenue_chart_url = ChartGenerator.generate_revenue_chart(
        list(reversed(revenue_data)), lot_names
    )
    
    # Comprehensive reservations summary table
    all_reservations = db.session.query(Reservation).join(
        ParkingSpot, Reservation.spot_id == ParkingSpot.id
    ).join(
        ParkingLot, ParkingSpot.lot_id == ParkingLot.id
    ).join(
        User, Reservation.user_id == User.id
    ).order_by(Reservation.parking_timestamp.desc()).limit(100).all()
    
    return render_template('admin_summary.html',
                         occupancy_chart_url=occupancy_chart_url,
                         revenue_chart_url=revenue_chart_url,
                         all_reservations=all_reservations)



@app.route('/create_lot', methods=['GET', 'POST'])
@login_required
def create_lot():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        lot = ParkingLot(
            prime_location_name=request.form['location_name'],
            address=request.form['address'],
            pin_code=request.form['pin_code'],
            price=float(request.form['price']),
            maximum_number_of_spots=int(request.form['max_spots'])
        )
        db.session.add(lot)
        db.session.flush()
        
        # Create parking spots
        create_parking_spots(lot.id, lot.maximum_number_of_spots)
        
        db.session.commit()
        flash('Parking lot created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_lot.html')

@app.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
@login_required
def edit_lot(lot_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    
    if request.method == 'POST':
        lot.prime_location_name = request.form['location_name']
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        lot.price = float(request.form['price'])
        
        new_max_spots = int(request.form['max_spots'])
        current_spots = len(lot.spots)
        
        if new_max_spots > current_spots:
            # Add new spots
            for i in range(current_spots + 1, new_max_spots + 1):
                spot = ParkingSpot(
                    lot_id=lot.id,
                    spot_number=f"A{i:03d}",
                    status='A'
                )
                db.session.add(spot)
        elif new_max_spots < current_spots:
            # Remove spots (only available ones)
            spots_to_remove = current_spots - new_max_spots
            available_spots = ParkingSpot.query.filter_by(
                lot_id=lot.id, status='A'
            ).limit(spots_to_remove).all()
            
            if len(available_spots) < spots_to_remove:
                flash('Cannot reduce spots: some spots are occupied!', 'error')
                return render_template('edit_lot.html', lot=lot)
            
            for spot in available_spots:
                db.session.delete(spot)
        
        lot.maximum_number_of_spots = new_max_spots
        db.session.commit()
        flash('Parking lot updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_lot.html', lot=lot)

@app.route('/delete_confirmation/<int:lot_id>')
@login_required
def delete_confirmation(lot_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    
    # Check if any spots are occupied
    occupied_count = len([s for s in lot.spots if s.status == 'O'])
    if occupied_count > 0:
        flash('Cannot delete lot: some spots are occupied!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('delete_confirmation.html', lot=lot)

@app.route('/confirm_delete_lot', methods=['POST'])
@login_required
def confirm_delete_lot():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    lot_id = request.form['lot_id']
    lot = ParkingLot.query.get_or_404(lot_id)
    
    db.session.delete(lot)
    db.session.commit()
    
    flash('Parking lot deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/spot_view/<int:spot_id>')
@login_required
def spot_view(spot_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    spot = ParkingSpot.query.get_or_404(spot_id)
    
    if spot.status == 'O':
        return redirect(url_for('spot_occupied', spot_id=spot_id))
    
    return render_template('spot_view.html', spot=spot)

@app.route('/spot_occupied/<int:spot_id>')
@login_required
def spot_occupied(spot_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    spot = ParkingSpot.query.get_or_404(spot_id)
    reservation = spot.get_current_reservation()
    
    if not reservation:
        return redirect(url_for('spot_view', spot_id=spot_id))
    
    # Calculate current estimated cost
    current_time = datetime.utcnow()
    duration = current_time - reservation.parking_timestamp
    est_hours = max(1, math.ceil(duration.total_seconds() / 3600))
    est_cost = est_hours * spot.lot.price
    
    return render_template('spot_occupied.html', 
                         spot=spot, 
                         reservation=reservation,
                         current_time=current_time,
                         estimated_cost=round(est_cost, 2),
                         estimated_hours=est_hours)


@app.route('/delete_spot/<int:spot_id>')
@login_required
def delete_spot(spot_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    spot = ParkingSpot.query.get_or_404(spot_id)
    
    # Check if spot is currently occupied
    if spot.status == 'O':
        flash('Cannot delete spot: it is currently occupied!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Check for active reservations
    active_reservations = [r for r in spot.reservations if r.is_active]
    if active_reservations:
        flash('Cannot delete spot: it has active reservations!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Store the lot and reservation info before deletion
    lot = spot.lot
    reservation_count = len(spot.reservations)
    
    # Update all reservations to preserve historical data
    for reservation in spot.reservations:
        # Store spot and lot information in the reservation for historical purposes
        reservation.spot_number = spot.spot_number
        reservation.lot_name = lot.prime_location_name
        # Set spot_id to None to break the relationship
        reservation.spot_id = None
    
    # Now safe to delete the spot
    db.session.delete(spot)
    
    # Update lot max spots
    lot.maximum_number_of_spots -= 1
    
    try:
        db.session.commit()
        if reservation_count > 0:
            flash(f'Parking spot deleted successfully! Historical data for {reservation_count} reservations preserved.', 'success')
        else:
            flash('Parking spot deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting spot. Please try again.', 'error')
    
    return redirect(url_for('admin_dashboard'))



@app.route('/user_analytics/<int:user_id>')
@login_required
def user_analytics(user_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Force refresh from database
    db.session.refresh(user)
    
    # Get daily spending data grouped by location and date
    daily_location_spending = {}
    
    for reservation in user.reservations:
        if reservation.parking_cost and not reservation.is_active:
            date_str = reservation.parking_timestamp.strftime('%Y-%m-%d')
            location = reservation.spot.lot.prime_location_name
            
            if date_str not in daily_location_spending:
                daily_location_spending[date_str] = {}
            
            if location not in daily_location_spending[date_str]:
                daily_location_spending[date_str][location] = 0
            
            daily_location_spending[date_str][location] += reservation.parking_cost
    
    # Get all unique locations for consistent coloring
    all_locations = set()
    for day_data in daily_location_spending.values():
        all_locations.update(day_data.keys())
    all_locations = sorted(list(all_locations))
    
    # Prepare data for stacked chart
    chart_data = {
        'dates': sorted(daily_location_spending.keys()),
        'locations': all_locations,
        'spending_by_location': {}
    }
    
    # Initialize spending arrays for each location
    for location in all_locations:
        chart_data['spending_by_location'][location] = []
    
    # Fill spending data for each date
    for date in chart_data['dates']:
        for location in all_locations:
            amount = daily_location_spending.get(date, {}).get(location, 0)
            chart_data['spending_by_location'][location].append(round(amount, 2))
    
    # Generate spending chart using matplotlib
    spending_chart_url = ChartGenerator.generate_user_spending_chart(chart_data)
    
    # Monthly spending data for additional analysis
    monthly_data = []
    for i in range(12):
        month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        
        monthly_spending = db.session.query(func.sum(Reservation.parking_cost)).filter(
            and_(
                Reservation.user_id == user_id,
                Reservation.parking_timestamp >= month_start,
                Reservation.parking_timestamp < month_end,
                Reservation.parking_cost.isnot(None),
                Reservation.is_active == False
            )
        ).scalar() or 0
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'spending': round(monthly_spending, 2)
        })
    
    return render_template('user_analytics.html',
                         user=user,
                         spending_chart_url=spending_chart_url,
                         chart_data=chart_data,
                         monthly_data=list(reversed(monthly_data)))

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        current_user.full_name = request.form['full_name']
        current_user.email     = request.form['email']
        current_user.phone     = request.form['phone']
        current_user.address   = request.form['address']
        current_user.pin_code  = request.form['pin_code']
        # Optionally allow password change:
        new_pw = request.form.get('password')
        if new_pw:
            current_user.password = generate_password_hash(new_pw)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_dashboard'))

    return render_template('edit_profile.html')

# ═══════════════════════════════════════════════════════════════
# APPLICATION STARTUP
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    init_database()
    app.run(debug=True)
