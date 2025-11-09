# Simple chart generator for parking management system
import matplotlib
matplotlib.use('Agg')  # Use backend that doesn't need display
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

# Set style for nice looking charts
plt.style.use('seaborn-v0_8')

class ChartGenerator:
    
    @staticmethod
    def generate_occupancy_chart(occupancy_data, lots):
        """Create a line chart showing how busy each parking lot is over time"""
        # Create a new chart with specific size
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Get the dates from our data
        dates = []
        for item in occupancy_data:
            dates.append(item['date'])
        
        # Colors for different parking lots
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        
        # Draw a line for each parking lot
        for i, lot_name in enumerate(lots):
            occupancy_rates = []
            
            # Calculate occupancy rate for each day
            for day in occupancy_data:
                # Find data for this specific lot
                lot_data = None
                for lot in day['lots']:
                    if lot['name'] == lot_name:
                        lot_data = lot
                        break
                
                # Calculate occupancy percentage
                if lot_data and lot_data['total'] > 0:
                    rate = (lot_data['occupied'] / lot_data['total']) * 100
                else:
                    rate = 0
                occupancy_rates.append(rate)
            
            # Draw the line for this parking lot
            ax.plot(dates, occupancy_rates, 
                   marker='o', linewidth=2, markersize=4,
                   color=colors[i % len(colors)], label=lot_name)
        
        # Set chart titles and labels
        ax.set_title('Daily Occupancy by Parking Lot', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Occupancy Rate (%)', fontsize=12)
        ax.set_ylim(0, 100)  # Y-axis from 0 to 100%
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)  # Add grid lines
        
        # Rotate date labels so they don't overlap
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Create folder if it doesn't exist and save chart
        chart_path = 'static/charts/occupancy_chart.png'
        os.makedirs('static/charts', exist_ok=True)
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return '/static/charts/occupancy_chart.png'
    
    @staticmethod
    def generate_revenue_chart(revenue_data, lots):
        """Create a stacked bar chart showing daily revenue from each parking lot"""
        # Create a new chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Get dates from data
        dates = []
        for item in revenue_data:
            dates.append(item['date'])
        
        # Colors for different parking lots
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        
        # Create array to stack bars on top of each other
        bottom = np.zeros(len(dates))
        
        # Create a bar for each parking lot
        for i, lot_name in enumerate(lots):
            revenues = []
            
            # Get revenue for each day
            for day in revenue_data:
                # Find data for this specific lot
                lot_data = None
                for lot in day['lots']:
                    if lot['name'] == lot_name:
                        lot_data = lot
                        break
                
                revenue = lot_data['revenue'] if lot_data else 0
                revenues.append(revenue)
            
            # Draw the bar for this parking lot
            ax.bar(dates, revenues, bottom=bottom, 
                  color=colors[i % len(colors)], label=lot_name)
            
            # Add this lot's revenue to bottom for stacking
            for j in range(len(bottom)):
                bottom[j] = bottom[j] + revenues[j]
        
        # Set chart titles and labels
        ax.set_title('Daily Revenue by Parking Lot', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Revenue (₹)', fontsize=12)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Format y-axis to show rupee symbol
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:.0f}'))
        
        # Rotate date labels
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save chart
        chart_path = 'static/charts/revenue_chart.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return '/static/charts/revenue_chart.png'
    
    @staticmethod
    def generate_user_location_chart(location_bookings):
        """Create a bar chart showing which locations a user visits most"""
        # Check if we have data
        if not location_bookings:
            return None
            
        # Create new chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Split the data into locations and counts
        locations = []
        counts = []
        for item in location_bookings:
            locations.append(item[0])  # Location name
            counts.append(item[1])     # Number of visits
        
        # Create bars
        bars = ax.bar(locations, counts, color='#36A2EB', alpha=0.7)
        
        # Add numbers on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        # Set chart titles and labels
        ax.set_title('Booking Frequency by Location', fontsize=16, fontweight='bold')
        ax.set_xlabel('Parking Location', fontsize=12)
        ax.set_ylabel('Number of Bookings', fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Rotate location names so they don't overlap
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save chart
        chart_path = 'static/charts/user_location_chart.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return '/static/charts/user_location_chart.png'
    
    @staticmethod
    def generate_user_duration_chart(duration_data):
        """Create a pie chart showing how long a user parks each day"""
        # Check if we have data
        if not duration_data:
            return None
        
        # Create new chart
        fig, ax = plt.subplots(figsize=(10, 8))
    
        # Get dates and hours from data
        dates = []
        hours = []
        for item in duration_data:
            dates.append(item['date'])
            hours.append(item['hours'])
    
        # Decide if we should show minutes or hours
        max_duration = 0
        for hour in hours:
            if hour > max_duration:
                max_duration = hour
        
        use_minutes = max_duration < 1.0  # If less than 1 hour, show minutes
    
        if use_minutes:
            # Convert hours to minutes for display
            values = []
            labels = []
            for i in range(len(hours)):
                minutes = hours[i] * 60
                values.append(minutes)
                labels.append(f'{dates[i]}\n{int(minutes)}m')
            unit = 'minutes'
            title = 'Daily Parking Duration Distribution (Minutes)'
        else:
            # Keep as hours
            values = hours
            labels = []
            for i in range(len(hours)):
                labels.append(f'{dates[i]}\n{hours[i]:.1f}h')
            unit = 'hours'
            title = 'Daily Parking Duration Distribution (Hours)'
    
        # Create colors for pie slices
        colors = plt.cm.Set3(range(len(values)))
    
        # Create the pie chart
        wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                     colors=colors, startangle=90,
                                     textprops={'fontsize': 10})
    
        # Set chart title
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
        # Make percentage text bold and white
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
    
        # Make pie chart circular
        ax.axis('equal')
    
        plt.tight_layout()
    
        # Save chart
        chart_path = 'static/charts/user_duration_chart.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
    
        return '/static/charts/user_duration_chart.png'

    @staticmethod
    def generate_user_spending_chart(chart_data):
        """Create a stacked bar chart showing daily spending by location"""
        # Check if we have data
        if not chart_data['dates']:
            return None
            
        # Create new chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        dates = chart_data['dates']
        locations = chart_data['locations']
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        
        # Create array to stack bars
        bottom = np.zeros(len(dates))
        
        # Create a bar for each location
        for i, location in enumerate(locations):
            spending = chart_data['spending_by_location'][location]
            
            # Draw bar for this location
            ax.bar(dates, spending, bottom=bottom, 
                  color=colors[i % len(colors)], label=location)
            
            # Add this location's spending to bottom for stacking
            for j in range(len(bottom)):
                bottom[j] = bottom[j] + spending[j]
        
        # Set chart titles and labels
        ax.set_title('Daily Spending Breakdown by Parking Location', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Spending (₹)', fontsize=12)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Format y-axis to show rupee symbol
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:.0f}'))
        
        # Rotate date labels
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save chart
        chart_path = 'static/charts/user_spending_chart.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return '/static/charts/user_spending_chart.png'
