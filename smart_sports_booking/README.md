# TurfZone - Smart Sports Booking Platform

A production-ready Flask web application for booking sports grounds and turfs with integrated payment processing and real-time API data.

## 🎯 Features

### Core Functionality
- ✅ **User Authentication**: Secure registration and login system
- ✅ **Sports Ground Booking**: Browse and book available sports grounds
- ✅ **Payment Integration**: Razorpay payment gateway with secure verification
- ✅ **Real-time Ground Data**: Integration with sports ground APIs (JustDial, Google Places, etc.)
- ✅ **Booking Management**: View, cancel, and manage your bookings
- ✅ **Peak Hours Analytics**: Analyze booking patterns and popular time slots
- ✅ **Production-Ready UI**: Professional header/footer and responsive design
- ✅ **Payment Status Tracking**: Pending, Completed, and Failed status tracking

### Technical Highlights
- **Framework**: Flask 2.3.2 with SQLAlchemy ORM
- **Payment**: Razorpay with signature verification
- **Database**: SQLite with proper relationships
- **Frontend**: Jinja2 templates with CSS Grid and Flexbox
- **API Integration**: External ground data sources with caching
- **Security**: CSRF protection, password hashing, HTTPS ready

## 📋 Project Structure

```
smart_sports_booking/
├── app.py                          # Main Flask application
├── seed_with_payments.py           # Demo data seeding script
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment configuration template
├── instance/                       # Instance folder
│   └── sports_booking.db          # SQLite database (auto-created)
├── templates/                      # Jinja2 HTML templates
│   ├── base.html                  # Master template with header/footer
│   ├── grounds.html               # Browse grounds
│   ├── booking_form.html          # Create bookings
│   ├── login.html                 # User login
│   ├── register.html              # User registration
│   ├── my_bookings.html           # Booking dashboard
│   ├── analytics.html             # Peak hours analytics
│   ├── payment.html               # Razorpay checkout
│   ├── payment_success.html       # Payment confirmation
│   └── payment_failed.html        # Payment error handling
└── PAYMENT_AND_API_SETUP.md       # Detailed setup guide
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Razorpay account (https://razorpay.com)

### Installation

1. **Clone and Navigate**
```bash
cd /workspaces/practice/smart_sports_booking
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup Environment Variables**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
# Add your Razorpay test keys from: https://dashboard.razorpay.com
```

4. **Seed Demo Data**
```bash
python seed_with_payments.py
```

5. **Run the Application**
```bash
python app.py
```

6. **Access the Application**
```
http://localhost:5000
```

## 💻 Demo Credentials

After running `seed_with_payments.py`, use these to login:

| Username | Email | Password |
|----------|-------|----------|
| rahul_kumar | rahul@example.com | password123 |
| priya_sharma | priya@example.com | password123 |
| amit_patel | amit@example.com | password123 |

## 💳 Testing Payments

Use these test cards with Razorpay:

| Card Number | Expiry | CVV |
|-------------|--------|-----|
| 4111111111111111 | Any Future | Any |
| 5555555555554444 | Any Future | Any |

## 🔧 Configuration

### Environment Variables (.env)

```env
# Razorpay Keys (get from https://dashboard.razorpay.com)
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=test_secret_key_xxxxxxxxxxxxx

# External APIs
JUSTDIAL_API_KEY=your_api_key
GOOGLE_PLACES_API_KEY=your_api_key

# Flask Configuration
SECRET_KEY=your-super-secret-key
FLASK_ENV=development
DEBUG=True
```

## 📊 Database Models

### User Model
```python
- id (Integer, Primary Key)
- username (String, Unique)
- email (String, Unique)
- password_hash (String)
- created_at (DateTime)
```

### Ground Model
```python
- id (Integer, Primary Key)
- name (String)
- sport_type (String) - Football, Cricket, Badminton, Tennis, etc.
- location (String)
- price_per_hour (Integer) - in paise
- contact_phone (String)
- amenities (String) - comma-separated
- rating (Float)
- external_api_id (String) - Track source API
- status (String) - Available/Booked
```

### Booking Model
```python
- id (Integer, Primary Key)
- user_id (Foreign Key)
- ground_id (Foreign Key)
- booking_date (String)
- time_slot (String)
- payment_status (String) - Pending/Completed/Failed
- payment_id (String)
- total_amount (Integer) - in paise
- created_at (DateTime)
```

### Payment Model
```python
- id (Integer, Primary Key)
- booking_id (Foreign Key)
- razorpay_order_id (String, Unique)
- razorpay_payment_id (String)
- razorpay_signature (String)
- amount (Integer) - in paise
- status (String) - pending/success/failed
- created_at (DateTime)
```

## 🌐 API Endpoints

### Authentication
```
POST   /register                    → User registration
POST   /login                       → User login
GET    /logout                      → User logout
```

### Grounds
```
GET    /                            → Homepage
GET    /grounds                     → Browse all grounds
GET    /api/grounds/search          → Search grounds by location/sport/price
POST   /api/sync-grounds            → Sync from external APIs
```

### Bookings
```
GET    /booking/<ground_id>         → Get booking form
POST   /booking/<ground_id>         → Create booking
GET    /my-bookings                 → View user bookings
POST   /cancel-booking/<booking_id> → Cancel booking
```

### Payments
```
GET    /payment/<booking_id>        → Initiate payment
POST   /payment/verify              → Verify payment signature
GET    /payment/success/<booking_id> → Success page
GET    /payment/failed/<booking_id>  → Failed page
```

### Analytics
```
GET    /analytics                   → Peak hours analytics
```

## 🔐 Security Features

- ✅ Password hashing with Werkzeug
- ✅ CSRF protection on forms
- ✅ Razorpay signature verification
- ✅ Environment variables for sensitive keys
- ✅ Flask-Login session management
- ✅ SQL injection protection via SQLAlchemy ORM
- ✅ HTTPS ready (set PREFERRED_URL_SCHEME=https in production)

## 🚀 Production Deployment

### Prerequisites
- Production Razorpay keys
- PostgreSQL database (recommended)
- SSL certificate for HTTPS
- Gunicorn or similar WSGI server

### Steps

1. **Update Requirements for Production**
```bash
pip install gunicorn
```

2. **Configure Production Environment**
```bash
export FLASK_ENV=production
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
export RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
export RAZORPAY_KEY_SECRET=your_production_secret
export DATABASE_URL=postgresql://user:password@host/db
```

3. **Run with Gunicorn**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

4. **Enable HTTPS**
- Use a reverse proxy (nginx, Apache)
- Install SSL certificate (Let's Encrypt recommended)
- Set `PREFERRED_URL_SCHEME=https` in app config

5. **Database Migration**
- Use Alembic for schema migrations in production
- Always backup database before updates

## 🧪 Testing

### Manual Testing Workflow
1. **Register a new account**
   - Go to /register
   - Create user with unique email/username

2. **Browse and book a ground**
   - Visit /grounds
   - Click "Book Now" on any ground
   - Select date and time slot

3. **Make a payment**
   - Click "Pay Now"
   - Use test card: 4111111111111111
   - Complete checkout

4. **Verify booking**
   - Go to "My Bookings"
   - Check payment status shows "Completed"

5. **Test API endpoints**
```bash
# Search grounds
curl "http://localhost:5000/api/grounds/search?location=Mumbai&sport_type=Football"

# Sync grounds from API
curl -X POST http://localhost:5000/api/sync-grounds
```

## 📚 API Integration Guide

See [PAYMENT_AND_API_SETUP.md](PAYMENT_AND_API_SETUP.md) for:
- Razorpay account setup
- Real turf API integration (JustDial, Google Places)
- Complete implementation examples
- Troubleshooting guide

## 🐛 Troubleshooting

### Issue: "Razorpay key not found"
**Solution**: Check .env file exists and has correct RAZORPAY_KEY_ID

### Issue: Database locked
**Solution**: Delete `instance/sports_booking.db` and restart app

### Issue: Port 5000 already in use
**Solution**: 
```bash
# Use different port
python app.py --port 5001
# Or kill the process using port 5000
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Issue: Templates not loading
**Solution**: Ensure templates folder exists with all .html files

### Issue: Payment verification fails
**Solution**: Verify RAZORPAY_KEY_SECRET is correct and matches API key

## 📞 Support

- **Documentation**: [PAYMENT_AND_API_SETUP.md](PAYMENT_AND_API_SETUP.md)
- **Flask Docs**: https://flask.palletsprojects.com
- **Razorpay Docs**: https://razorpay.com/docs
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org

## 📝 Environment Variables Reference

```bash
# Payment Processing
RAZORPAY_KEY_ID              # Public key from Razorpay dashboard
RAZORPAY_KEY_SECRET          # Secret key from Razorpay dashboard

# External APIs
JUSTDIAL_API_KEY             # JustDial sports grounds API key
GOOGLE_PLACES_API_KEY        # Google Places API key
SPORTS_API_KEY               # Custom sports API key

# Flask Configuration
SECRET_KEY                   # Random secret for session encryption
FLASK_ENV                    # 'development' or 'production'
DEBUG                        # True/False for debug mode
DATABASE_URL                 # PostgreSQL URL for production
PREFERRED_URL_SCHEME         # 'https' for production
```

## 📈 Monitoring & Analytics

The `/analytics` endpoint provides:
- Peak booking hours
- Most popular sports types
- Ground utilization rates
- Payment success metrics

## ✅ Production Checklist

- [ ] Setup Razorpay production account
- [ ] Generate strong SECRET_KEY
- [ ] Configure PostgreSQL database
- [ ] Enable HTTPS/SSL
- [ ] Setup environment variables
- [ ] Configure email notifications
- [ ] Setup logging and monitoring
- [ ] Load test application
- [ ] Setup automated backups
- [ ] Document runbook for deployment

## 🎓 Learning Resources

This project demonstrates:
- Flask web application architecture
- SQLAlchemy ORM and database relationships
- Payment gateway integration
- RESTful API design
- Jinja2 template inheritance
- Frontend form handling
- User authentication
- Error handling and logging
- Production deployment best practices

## 📄 License

This project is for educational and commercial purposes.

## 👨‍💻 Contributing

Feel free to fork, modify, and deploy for your own sports booking platform!

---

**Last Updated**: August 2024
**Version**: 1.0.0
**Status**: Production Ready ✅
