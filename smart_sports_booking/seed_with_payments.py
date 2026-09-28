#!/usr/bin/env python
"""
Seed script to populate the database with sample data and demo payments
Usage: python seed_with_payments.py
"""

from app import app, db, Ground, User, Booking, Payment
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def clear_database():
    """Clear all data from database"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✓ Database cleared and recreated")

def seed_users():
    """Add sample users"""
    with app.app_context():
        users = [
            User(
                username='rahul_kumar',
                email='rahul@example.com',
                password_hash=generate_password_hash('password123')
            ),
            User(
                username='priya_sharma',
                email='priya@example.com',
                password_hash=generate_password_hash('password123')
            ),
            User(
                username='amit_patel',
                email='amit@example.com',
                password_hash=generate_password_hash('password123')
            )
        ]
        
        for user in users:
            db.session.add(user)
        
        db.session.commit()
        print(f"✓ Added {len(users)} sample users")

def seed_grounds():
    """Add sample sports grounds with real-like data"""
    with app.app_context():
        grounds = [
            Ground(
                name='SportZone Football Academy',
                sport_type='Football',
                location='Mumbai, Maharashtra',
                price_per_hour=800,
                contact_phone='9876543210',
                amenities='lights,parking,changing_room,cafeteria',
                rating=4.8,
                status='Available',
                external_api_id='justdial_001'
            ),
            Ground(
                name='Elite Cricket Grounds',
                sport_type='Cricket',
                location='Pune, Maharashtra',
                price_per_hour=1200,
                contact_phone='9876543211',
                amenities='lights,parking,cafeteria',
                rating=4.6,
                status='Available',
                external_api_id='justdial_002'
            ),
            Ground(
                name='Badminton Indoor Courts',
                sport_type='Badminton',
                location='Bangalore, Karnataka',
                price_per_hour=500,
                contact_phone='9876543212',
                amenities='indoor,parking,changing_room',
                rating=4.5,
                status='Available',
                external_api_id='google_001'
            ),
            Ground(
                name='Tennis Championship Court',
                sport_type='Tennis',
                location='Delhi, Delhi',
                price_per_hour=1500,
                contact_phone='9876543213',
                amenities='lights,parking,pro_coaching',
                rating=4.9,
                status='Available',
                external_api_id='google_002'
            ),
            Ground(
                name='Basketball Premium Arena',
                sport_type='Basketball',
                location='Hyderabad, Telangana',
                price_per_hour=700,
                contact_phone='9876543214',
                amenities='indoor,lights,parking',
                rating=4.4,
                status='Available',
                external_api_id='api_001'
            ),
            Ground(
                name='Volleyball Sports Complex',
                sport_type='Volleyball',
                location='Chennai, Tamil Nadu',
                price_per_hour=600,
                contact_phone='9876543215',
                amenities='indoor,parking,changing_room',
                rating=4.3,
                status='Available',
                external_api_id='api_002'
            ),
            Ground(
                name='Hockey Training Ground',
                sport_type='Hockey',
                location='Kolkata, West Bengal',
                price_per_hour=900,
                contact_phone='9876543216',
                amenities='outdoor,lights,parking,coaching',
                rating=4.7,
                status='Available',
                external_api_id='custom_001'
            ),
            Ground(
                name='Squash Premium Club',
                sport_type='Squash',
                location='Bangalore, Karnataka',
                price_per_hour=1100,
                contact_phone='9876543217',
                amenities='indoor,changing_room,cafeteria',
                rating=4.6,
                status='Available',
                external_api_id='custom_002'
            )
        ]
        
        for ground in grounds:
            db.session.add(ground)
        
        db.session.commit()
        print(f"✓ Added {len(grounds)} sample sports grounds")

def seed_bookings_and_payments():
    """Add sample bookings with payment status"""
    with app.app_context():
        # Get users and grounds
        users = User.query.all()
        grounds = Ground.query.all()
        
        if not users or not grounds:
            print("✗ No users or grounds found. Please seed them first.")
            return
        
        bookings = []
        payments = []
        
        # Create sample bookings with different payment statuses
        today = datetime.now()
        
        # Booking 1: Completed payment
        booking1 = Booking(
            user_id=users[0].id,
            ground_id=grounds[0].id,
            booking_date=(today + timedelta(days=2)).strftime('%Y-%m-%d'),
            time_slot='06:00-07:00',
            payment_status='Completed',
            total_amount=80000,  # ₹800 in paise
            payment_id='pay_demo_001'
        )
        db.session.add(booking1)
        db.session.flush()
        
        payment1 = Payment(
            booking_id=booking1.id,
            user_id=users[0].id,
            razorpay_order_id='order_001',
            razorpay_payment_id='pay_demo_001',
            razorpay_signature='demo_sig_001',
            amount=80000,
            status='success'
        )
        payments.append(payment1)
        
        # Booking 2: Pending payment
        booking2 = Booking(
            user_id=users[1].id,
            ground_id=grounds[1].id,
            booking_date=(today + timedelta(days=3)).strftime('%Y-%m-%d'),
            time_slot='18:00-19:00',
            payment_status='Pending',
            total_amount=120000,  # ₹1200 in paise
        )
        db.session.add(booking2)
        db.session.flush()
        
        payment2 = Payment(
            booking_id=booking2.id,
            user_id=users[1].id,
            razorpay_order_id='order_002',
            amount=120000,
            status='pending'
        )
        payments.append(payment2)
        
        # Booking 3: Failed payment
        booking3 = Booking(
            user_id=users[2].id,
            ground_id=grounds[2].id,
            booking_date=(today + timedelta(days=4)).strftime('%Y-%m-%d'),
            time_slot='19:00-20:00',
            payment_status='Failed',
            total_amount=50000,  # ₹500 in paise
        )
        db.session.add(booking3)
        db.session.flush()
        
        payment3 = Payment(
            booking_id=booking3.id,
            user_id=users[2].id,
            razorpay_order_id='order_003',
            razorpay_payment_id='pay_failed_001',
            amount=50000,
            status='failed'
        )
        payments.append(payment3)
        
        # Add more completed bookings
        booking4 = Booking(
            user_id=users[0].id,
            ground_id=grounds[3].id,
            booking_date=(today + timedelta(days=5)).strftime('%Y-%m-%d'),
            time_slot='17:00-18:00',
            payment_status='Completed',
            total_amount=150000,  # ₹1500 in paise
            payment_id='pay_demo_002'
        )
        db.session.add(booking4)
        db.session.flush()
        
        payment4 = Payment(
            booking_id=booking4.id,
            user_id=users[0].id,
            razorpay_order_id='order_004',
            razorpay_payment_id='pay_demo_002',
            razorpay_signature='demo_sig_002',
            amount=150000,
            status='success'
        )
        payments.append(payment4)
        
        # Add all payments
        for payment in payments:
            db.session.add(payment)
        
        db.session.commit()
        print(f"✓ Added 4 sample bookings with payment records")
        print(f"  - 2 completed payments")
        print(f"  - 1 pending payment")
        print(f"  - 1 failed payment")

def print_demo_credentials():
    """Print demo login credentials"""
    print("\n" + "="*60)
    print("📝 DEMO CREDENTIALS")
    print("="*60)
    print("\nYou can login with any of these credentials:\n")
    
    users_data = [
        ('rahul_kumar', 'rahul@example.com', 'password123'),
        ('priya_sharma', 'priya@example.com', 'password123'),
        ('amit_patel', 'amit@example.com', 'password123'),
    ]
    
    for username, email, password in users_data:
        print(f"Username: {username}")
        print(f"Email:    {email}")
        print(f"Password: {password}")
        print()
    
    print("="*60)
    print("💳 RAZORPAY TEST CARDS")
    print("="*60)
    print("\nCard Number: 4111111111111111")
    print("CVV:         Any")
    print("Expiry:      Any future date")
    print("\nCard Number: 5555555555554444")
    print("CVV:         Any")
    print("Expiry:      Any future date")
    print("="*60 + "\n")

def main():
    """Run all seed operations"""
    print("\n🌱 Starting Database Seeding...\n")
    
    clear_database()
    seed_users()
    seed_grounds()
    seed_bookings_and_payments()
    
    print_demo_credentials()
    
    print("✅ Database seeding completed successfully!")
    print("\n🚀 You can now run the Flask app:")
    print("   python app.py\n")

if __name__ == '__main__':
    main()
