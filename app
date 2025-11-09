# Simple database models for parking management system
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import math

# Create database connection
db = SQLAlchemy()

# ═══════════════════════════════════════════════════════════════
# USER TABLE - People who use our parking system
# ═══════════════════════════════════════════════════════════════
class User(UserMixin, db.Model):
    # Basic user information
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Connection to reservations (one user can have many reservations)
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    
    def get_total_spending(self):
        """Calculate how much money this user has spent"""
        total = 0.0
        for reservation in self.reservations:
            if reservation.parking_cost and not reservation.is_active:
                total = total + reservation.parking_cost
        return round(total, 2)
    
    def get_total_hours(self):
        """Calculate total hours this user has been charged for"""
        total_hours = 0
        for reservation in self.reservations:
            if reservation.hours_charged and not reservation.is_active:
                total_hours = total_hours + reservation.hours_charged
        return total_hours
    
    def get_parking_frequency(self):
        """Count how many times this user has parked (completed sessions)"""
        count = 0
        for reservation in self.reservations:
            if not reservation.is_active:
                count = count + 1
        return count
    
    def get_favorite_location(self):
        """Find which parking lot this user uses most often"""
        location_count = {}
        
        # Count visits to each location
        for reservation in self.reservations:
            if not reservation.is_active and reservation.spot and reservation.spot.lot:
                location_name = reservation.spot.lot.prime_location_name
                if location_name in location_count:
                    location_count[location_name] = location_count[location_name] + 1
                else:
                    location_count[location_name] = 1
        
        # Find the location with the highest count
        if location_count:
            max_count = 0
            favorite_location = "No parking history"
            for location, count in location_count.items():
                if count > max_count:
                    max_count = count
                    favorite_location = location
            return favorite_location
        else:
            return "No parking history"

# ═══════════════════════════════════════════════════════════════
# PARKING LOT TABLE - Different parking locations
# ═══════════════════════════════════════════════════════════════
class ParkingLot(db.Model):
    # Basic parking lot information
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Connection to parking spots (one lot has many spots)
    spots = db.relationship('ParkingSpot', backref='lot', lazy=True, cascade='all, delete-orphan')
    
    def get_occupancy_stats(self):
        """Calculate how many spots are occupied vs available right now"""
        total_spots = len(self.spots)
        occupied_spots = 0
        
        # Count how many spots are occupied
        for spot in self.spots:
            if spot.status == 'O':  # 'O' means Occupied
                occupied_spots = occupied_spots + 1
        
        available_spots = total_spots - occupied_spots
        
        # Calculate occupancy percentage
        if total_spots > 0:
            occupancy_rate = round((occupied_spots / total_spots * 100), 1)
        else:
            occupancy_rate = 0
        
        return {
            "total": total_spots,
            "occupied": occupied_spots,
            "available": available_spots,
            "occupancy_rate": occupancy_rate
        }
    
    def get_total_revenue(self):
        """Calculate total money earned from this parking lot (completed sessions only)"""
        total_revenue = 0.0
        
        # Go through each parking spot in this lot
        for spot in self.spots:
            # Go through each reservation for this spot
            for reservation in spot.reservations:
                # Only count completed reservations that have been paid
                if reservation.parking_cost and not reservation.is_active:
                    total_revenue = total_revenue + reservation.parking_cost
        
        return round(total_revenue, 2)
    
    def get_total_spots_ever_occupied(self):
        """Count unique spots that have been used at least once"""
        used_spots = 0
        for spot in self.spots:
            if len(spot.reservations) > 0:
                used_spots = used_spots + 1
        return used_spots

# ═══════════════════════════════════════════════════════════════
# PARKING SPOT TABLE - Individual parking spaces within a lot
# ═══════════════════════════════════════════════════════════════
class ParkingSpot(db.Model):
    # Basic spot information
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.String(10), nullable=False)  # Like A001, A002, etc.
    status = db.Column(db.String(1), default='A', nullable=False)  # 'A'=Available, 'O'=Occupied
    
    # Connection to reservations (one spot can have many reservations over time)
    reservations = db.relationship('Reservation', backref='spot', lazy=True)
    
    def get_current_reservation(self):
        """Find if someone is currently parked in this spot"""
        for reservation in self.reservations:
            if reservation.is_active:  # is_active = True means still parked
                return reservation
        return None  # No one is currently parked here

# ═══════════════════════════════════════════════════════════════
# RESERVATION TABLE - Records of parking sessions
# ═══════════════════════════════════════════════════════════════
class Reservation(db.Model):
    # Basic reservation information
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Vehicle information
    vehicle_license_plate = db.Column(db.String(20), nullable=False)
    vehicle_color = db.Column(db.String(20), nullable=False)
    
    # Time information
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    
    # Cost information
    parking_cost = db.Column(db.Float, nullable=True)
    hours_charged = db.Column(db.Integer, nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def calculate_cost(self, hourly_rate):
        """Calculate parking cost based on duration and hourly rate"""
        if not self.leaving_timestamp:
            return 0.0, 0
        
        # Calculate how long the car was parked (in hours)
        time_difference = self.leaving_timestamp - self.parking_timestamp
        duration_in_seconds = time_difference.total_seconds()
        duration_in_hours = duration_in_seconds / 3600  # Convert seconds to hours
        
        # Business rule: Always charge for at least 1 hour
        if duration_in_hours < 1:
            charged_hours = 1
        else:
            charged_hours = math.ceil(duration_in_hours)  # Round up to next hour
        
        # Calculate total cost
        total_cost = charged_hours * hourly_rate
        
        return round(total_cost, 2), charged_hours
    
    def get_duration_string(self):
        """Get parking duration in readable format like '2h 30m'"""
        # Determine end time
        if self.leaving_timestamp:
            end_time = self.leaving_timestamp
        else:
            end_time = datetime.utcnow()  # Still parked, use current time
        
        # Calculate time difference
        time_difference = end_time - self.parking_timestamp
        total_seconds = time_difference.total_seconds()
        
        # Convert to hours and minutes
        hours = int(total_seconds // 3600)  # 3600 seconds = 1 hour
        remaining_seconds = total_seconds % 3600
        minutes = int(remaining_seconds // 60)  # 60 seconds = 1 minute
        
        # Return formatted string
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
