# 🚗 Vehicle Parking Management System

A comprehensive web-based parking management system built with Flask that streamlines parking lot operations, user reservations, and provides detailed analytics through interactive charts.

## 📋 Project Overview

The Vehicle Parking Management System is designed to digitalize and automate parking operations. The system enables **administrators** to manage parking lots and monitor usage, while **users** can book parking spots, view their parking history, and manage their reservations efficiently.

### 🎯 Problem Statement
Traditional parking systems lack real-time monitoring, efficient booking mechanisms, and comprehensive analytics. This system addresses these challenges by providing a digital solution for parking management.

## ✨ Key Features

### 👨‍💼 Admin Features
- **Dashboard Management** - View all parking lots with real-time occupancy
- **Parking Lot Creation** - Add new parking locations with spot generation
- **User Management** - Monitor registered users and their activities
- **Analytics & Reports** - Visual charts showing occupancy, revenue, and trends
- **Spot Management** - Individual parking spot monitoring and control

### 👤 User Features
- **User Registration & Login** - Secure authentication system
- **Parking Spot Booking** - Real-time availability and booking
- **Reservation Management** - View active and historical parking sessions
- **Cost Calculation** - Automatic billing based on parking duration
- **Profile Management** - Update personal information
- **Usage Analytics** - Personal parking statistics and spending analysis

### 📊 Analytics & Visualization
- **Occupancy Charts** - Real-time parking lot utilization trends
- **Revenue Analysis** - Daily/monthly income tracking
- **User Behavior** - Location preferences and usage patterns
- **Duration Analysis** - Parking time distribution
- **Spending Breakdown** - Cost analysis by location and time

## 🛠️ Technologies Used

### Backend
- **Flask** - Python web framework for server-side logic
- **SQLAlchemy** - Database ORM for data management
- **Flask-Login** - User session management and authentication
- **SQLite** - Lightweight database for data storage

### Frontend
- **HTML5** - Structure and content markup
- **Bootstrap 5** - Responsive UI framework
- **CSS3** - Custom styling and animations

### Data Visualization
- **Matplotlib** - Chart generation for analytics
- **NumPy** - Numerical data processing for charts

### Development Tools
- **Python 3.12** - Programming language
- **Jinja2** - Template engine for dynamic content
- **Werkzeug** - WSGI utility library for password hashing

## 🏗️ Project Milestones

### Phase 1: Database Design & Models
-  Created User, ParkingLot, ParkingSpot, and Reservation models
-  Established database relationships and constraints
-  Implemented automatic spot generation system

### Phase 2: Authentication & User Management
-  User registration and login functionality
-  Role-based access control (Admin/User)
-  Session management and security

### Phase 3: Core Parking Operations
-  Parking lot creation and management
-  Real-time spot availability tracking
-  Booking and reservation system
-  Cost calculation with hourly billing

### Phase 4: User Interface & Experience
-  Responsive web design with Bootstrap
-  Interactive dashboards for users and admins
-  Real-time status updates and notifications

### Phase 5: Analytics & Reporting  
-  Chart generation using Matplotlib
-  Occupancy and revenue analytics
-  User behavior analysis
-  Visual data representation

### Phase 6: System Integration & Testing
-  Complete workflow testing
-  Error handling and validation
-  Performance optimization

## 🗃️ Database Models

### User Model
- id (Primary Key)
- username (Unique)
- password (Hashed)
- email
- phone
- full_name
- address
- pin_code
- is_admin (Boolean)
- registration_date

### ParkingLot Model
- id (Primary Key)
- prime_location_name
- address
- pin_code
- price (per hour)
- maximum_number_of_spots
- created_date

### ParkingSpot Model
- id (Primary Key)
- lot_id (Foreign Key)
- spot_number (e.g., A001, A002)
- status ('A' = Available, 'O' = Occupied)


### Reservation Model
- id (Primary Key)
- spot_id, user_id (Foreign Keys)
- vehicle_license_plate
- vehicle_color
- parking_timestamp
- leaving_timestamp
- parking_cost
- hours_charged
- is_active (Boolean)


## 📁 Project Structure
.
├──  README.md
├──  app.py
├── app 
│   ├── _ _init_ _.py
│   ├──  chart_generator.py
│   ├──  models.py
├──  instance
│   └── parking_app.db
├──  requirement.txt
├──  static
│   ├── charts
│   │   ├── occupancy_chart.png
│   │   ├── revenue_chart.png
│   │   ├── user_duration_chart.png
│   │   ├── user_location_chart.png
│   │   └── user_spending_chart.png
│   └── style.css
└──  templates
    ├──  admin_dashboard.html
    ├──  admin_summary.html
    ├──  admin_users.html
    ├──  base.html
    ├──  book_confirmation.html
    ├──  create_lot.html
    ├──  delete_confirmation.html
    ├──  edit_lot.html
    ├──  edit_profile.html
    ├──  login.html
    ├──  register.html
    ├──  release_confirmation.html
    ├──  spot_occupied.html
    ├──  spot_view.html
    ├──  user_analytics.html
    ├──  user_dashboard.html
    └──  user_summary.html


[ER Diagram](https://drive.google.com/file/d/1Hij9NO0yOwNv2RZEw_MUSvy8AJwe5bX3/view?usp=sharing)

## Architecture and Features

### Project Organization:

- app.py contains Flask routes (controllers), handling requests, user sessions, and business logic.
- models.py defines ORM classes representing Users, ParkingLots, Spots, and Reservations, with helper methods.
- chart_generator.py generates analytics charts using Matplotlib, saving static images for dashboard display.
- The templates directory holds Jinja2 templates rendering HTML data views with dynamic content.
- Static files (CSS, chart images) are inside static for UI styling and graph display.
- Data stored in SQLite database located in instance/.

### Features Implemented:

- Role-based user authentication distinguishing admins and normal users.
- Comprehensive parking lot management including lot creation, editing, and deletion.
- Automated parking spot number generation for each lot.
- Real-time spot availability and booking for users, with input validation.
- Reservation billing with hourly pricing, minimum charging, and automatic cost computation.
- Historical reservation viewing and management from dashboards.
- Rich data analytics with charts showing occupancy, revenue, user behavior, and spending trends.
- Safety checks prevent deletion of occupied spots or lots with active reservations.
- Responsive, professional UI using Bootstrap and FontAwesome icons.
- Error handling with informative flash messages.
