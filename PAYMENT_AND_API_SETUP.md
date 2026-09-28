# TurfZone - Payment & API Integration Guide

## 🎯 Payment Integration (Razorpay)

### Prerequisites
- Razorpay account: https://razorpay.com/
- Python 3.7+
- Flask application setup

### Step 1: Setup Razorpay Account

1. **Create Account**
   - Visit https://razorpay.com
   - Sign up and complete KYC verification
   - Go to Dashboard → Settings → API Keys

2. **Get Your Keys**
   - Copy your **Key ID** (Public key)
   - Copy your **Key Secret** (Private key)

### Step 2: Configure Environment Variables

Create a `.env` file in your project root:

```bash
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your_secret_key_here
SPORTS_API_KEY=your_api_key_for_grounds
```

Or set environment variables:

```bash
export RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
export RAZORPAY_KEY_SECRET=your_secret_key_here
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Update Database

The app automatically creates the Payment table on first run:

```python
with app.app_context():
    db.create_all()
```

## 💳 Payment Flow

1. **User creates booking** → Booking created with `payment_status='Pending'`
2. **User clicks "Pay Now"** → Redirected to payment page
3. **Payment page initialized** → Razorpay checkout form appears
4. **User completes payment** → Signature verification
5. **Payment verified** → Booking status changed to `Completed`
6. **User see success page** → With booking confirmation

## 🏟️ Real Turf/Ground API Integration

### Available APIs

#### 1. **JustDial API** (Recommended for India)
- API: https://api.justdial.com/
- Great for finding sports grounds in India
- Documentation: https://justdial.com/api

#### 2. **Google Places API**
- Search for sports grounds by location
- Get ratings, photos, contact info
- Setup: https://developers.google.com/maps/documentation/places

#### 3. **Custom Sports APIs**
- Bounce: https://www.bounce.co.in/api
- SportzWare: https://sportzware.com
- Custom platforms specific to your region

### Implementation Example

```python
# config.py
API_PROVIDERS = {
    'justdial': {
        'base_url': 'https://api.justdial.com/grounds',
        'key': os.environ.get('JUSTDIAL_API_KEY'),
    },
    'google_places': {
        'base_url': 'https://maps.googleapis.com/maps/api/place',
        'key': os.environ.get('GOOGLE_PLACES_API_KEY'),
    }
}
```

### How to Add Real Grounds

#### Option 1: Manual Entry
```python
# Create ground directly in database
ground = Ground(
    name='SportZone Football Field',
    sport_type='Football',
    location='Mumbai, Maharashtra',
    price_per_hour=800,
    contact_phone='9876543210',
    amenities='lights,parking,changing_room',
    rating=4.8,
    external_api_id='justdial_12345'
)
db.session.add(ground)
db.session.commit()
```

#### Option 2: API Sync
```python
# POST /api/sync-grounds
# Automatically syncs grounds from configured APIs
```

#### Option 3: Manual Upload
```bash
# CLI command to sync grounds
python seed.py --import-from-api justdial
```

## 🔌 API Endpoints

### Payment Endpoints

```
POST   /payment/<booking_id>           → Initiate payment
POST   /payment/verify                 → Verify payment signature
GET    /payment/success/<booking_id>   → Success page
GET    /payment/failed/<booking_id>    → Failed page
```

### Ground Search Endpoints

```
GET    /api/grounds/search?location=Mumbai&sport_type=Football&max_price=1000
       → Returns matching grounds

GET    /api/ground/<ground_id>/details
       → Get detailed ground info

POST   /api/sync-grounds
       → Sync grounds from external APIs
```

## 🛠️ Testing

### Test with Razorpay Test Keys

```env
RAZORPAY_KEY_ID=rzp_test_1234567890
RAZORPAY_KEY_SECRET=test_secret_key
```

### Test Payment Cards

| Card Number | CVV | Expiry |
|-------------|-----|--------|
| 4111111111111111 | Any | Any future date |
| 5555555555554444 | Any | Any future date |

### Test Flow

1. Create account and book a ground
2. Click "Pay Now"
3. Use test card numbers above
4. Complete the payment

## 📊 Database Models

### Payment Model

```python
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
    razorpay_order_id = db.Column(db.String(100), unique=True)
    razorpay_payment_id = db.Column(db.String(100))
    razorpay_signature = db.Column(db.String(255))
    amount = db.Column(db.Integer)  # in paise
    status = db.Column(db.String(20))  # pending, success, failed
```

### Updated Booking Model

```python
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ground_id = db.Column(db.Integer, db.ForeignKey('ground.id'))
    booking_date = db.Column(db.String(20))
    time_slot = db.Column(db.String(20))
    payment_status = db.Column(db.String(20))  # Pending, Completed, Failed
    payment_id = db.Column(db.String(100))
    total_amount = db.Column(db.Integer)  # in paise
```

### Ground Model (Enhanced)

```python
class Ground(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    sport_type = db.Column(db.String(50))
    location = db.Column(db.String(100))
    price_per_hour = db.Column(db.Integer)
    amenities = db.Column(db.String(255))  # comma-separated
    rating = db.Column(db.Float)
    contact_phone = db.Column(db.String(20))
    external_api_id = db.Column(db.String(100))  # Track API source
```

## 🚀 Production Deployment

### 1. Security Checklist

- [ ] Use environment variables for all sensitive keys
- [ ] Enable HTTPS only
- [ ] Set `Flask.debug = False`
- [ ] Update SECRET_KEY with strong random string
- [ ] Implement payment signature verification
- [ ] Add rate limiting to payment endpoints
- [ ] Enable CORS restrictions

### 2. Production Configuration

```python
# config.py - Production
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['RAZORPAY_KEY_ID'] = os.environ.get('RAZORPAY_KEY_ID')
app.config['RAZORPAY_KEY_SECRET'] = os.environ.get('RAZORPAY_KEY_SECRET')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
```

### 3. Enable Signature Verification

Uncomment in `app.py` verify_payment():

```python
import hmac
import hashlib

message = f"{order_id}|{payment_id}"
signature_check = hmac.new(
    app.config['RAZORPAY_KEY_SECRET'].encode(),
    message.encode(),
    hashlib.sha256
).hexdigest()

if signature_check == signature:
    # Payment verified
    pass
```

## 📞 Support & Documentation

- **Razorpay Docs**: https://razorpay.com/docs
- **Flask Docs**: https://flask.palletsprojects.com
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org

## ⚠️ Common Issues & Solutions

### Issue: Razorpay key not found
**Solution**: Check `.env` file and environment variables

### Issue: Payment verification fails
**Solution**: Ensure correct key order in HMAC-SHA256 verification

### Issue: Grounds not syncing from API
**Solution**: Check API endpoint and authentication key

### Issue: Database migration errors
**Solution**: Delete `sports_booking.db` and restart app

## 📝 Next Steps

1. ✅ Replace test keys with production Razorpay keys
2. ✅ Setup real ground APIs (JustDial, Google Places)
3. ✅ Configure email notifications for bookings
4. ✅ Add refund handling
5. ✅ Setup analytics dashboard
6. ✅ Deploy to production server

---

**Last Updated**: August 2024
**Version**: 1.0.0
