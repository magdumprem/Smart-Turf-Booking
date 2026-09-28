# TurfZone - Complete URL Reference Guide

All available routes and endpoints for the TurfZone sports booking platform.

---

## 🏠 Main Pages

| Path | Method | Purpose | Requires Auth |
|------|--------|---------|----------------|
| `/` | GET | Homepage | No |
| `/grounds` | GET | Browse all grounds | No |
| `/analytics` | GET | Peak hours analytics | Yes |

---

## 👤 Authentication

| Path | Method | Purpose | Requires Auth |
|------|--------|---------|----------------|
| `/register` | GET/POST | User registration | No |
| `/login` | GET/POST | User login | No |
| `/logout` | GET | User logout | Yes |

---

## 🎫 Bookings

| Path | Method | Purpose | Requires Auth |
|------|--------|---------|----------------|
| `/booking/<ground_id>` | GET | Show booking form | Yes |
| `/booking/<ground_id>` | POST | Create booking | Yes |
| `/my-bookings` | GET | View user's bookings | Yes |
| `/cancel-booking/<booking_id>` | POST | Cancel a booking | Yes |

---

## 💳 Payments

| Path | Method | Purpose | Requires Auth | Notes |
|------|--------|---------|----------------|-------|
| `/payment/<booking_id>` | GET | Show payment page | Yes | Initiate Razorpay |
| `/payment/verify` | POST | Verify payment | Yes | AJAX endpoint |
| `/payment/success/<booking_id>` | GET | Success page | Yes | After payment |
| `/payment/failed/<booking_id>` | GET | Failure page | Yes | If payment fails |

---

## 🔌 API Endpoints

### Search Grounds
```
GET /api/grounds/search
Parameters:
  - location (string): City/area name
  - sport_type (string): Type of sport
  - max_price (integer): Maximum price per hour (in paise)
  
Example:
GET /api/grounds/search?location=Mumbai&sport_type=Football&max_price=100000

Response:
{
  "grounds": [
    {
      "id": 1,
      "name": "SportZone Football Academy",
      "sport_type": "Football",
      "location": "Mumbai",
      "price_per_hour": 800,
      "rating": 4.8,
      "amenities": ["lights", "parking", "changing_room"]
    }
  ]
}
```

### Sync Grounds from External APIs
```
POST /api/sync-grounds
No parameters required

Response:
{
  "success": true,
  "grounds_added": 15,
  "message": "Synced 15 grounds from external APIs"
}
```

---

## 📊 Navigation Examples

### User Journey - Complete Booking Flow
1. **Browse** → `GET /grounds`
2. **Select Ground** → Click "Book Now" button
3. **Create Booking** → `POST /booking/<ground_id>`
4. **View My Bookings** → `GET /my-bookings`
5. **Make Payment** → `GET /payment/<booking_id>`
6. **Verify Payment** → `POST /payment/verify` (AJAX)
7. **See Confirmation** → `GET /payment/success/<booking_id>`

### Admin/Analytics Journey
1. **View Analytics** → `GET /analytics`
2. **Search Grounds** → `GET /api/grounds/search?location=...`
3. **Sync Data** → `POST /api/sync-grounds`

---

## 🔐 Protected Routes

These routes require user authentication (login):
- `/booking/<ground_id>` - GET/POST
- `/my-bookings` - GET
- `/cancel-booking/<booking_id>` - POST
- `/payment/<booking_id>` - GET
- `/payment/success/<booking_id>` - GET
- `/payment/failed/<booking_id>` - GET
- `/logout` - GET
- `/analytics` - GET

If you try accessing without login, you'll be redirected to `/login`

---

## 📝 Form Data Examples

### Registration (POST /register)
```json
{
  "username": "rahul_kumar",
  "email": "rahul@example.com",
  "password": "password123",
  "confirm_password": "password123"
}
```

### Login (POST /login)
```json
{
  "username": "rahul_kumar",
  "password": "password123"
}
```

### Create Booking (POST /booking/<ground_id>)
```json
{
  "booking_date": "2024-09-15",
  "time_slot": "18:00-19:00"
}
```

### Payment Verification (POST /payment/verify)
```json
{
  "razorpay_order_id": "order_123456",
  "razorpay_payment_id": "pay_123456",
  "razorpay_signature": "signature_hash"
}
```

---

## 🧪 Testing URLs

### Quick Test Sequence
1. Open browser: `http://localhost:5000`
2. Register: `http://localhost:5000/register`
3. Login: `http://localhost:5000/login`
4. Browse grounds: `http://localhost:5000/grounds`
5. Select any ground and click "Book Now"
6. View bookings: `http://localhost:5000/my-bookings`
7. Click "Pay Now" on any pending booking
8. Complete payment with test card: `4111111111111111`
9. View payment success: Should redirect to success page

---

## 🔍 API Testing with curl

### Search Grounds
```bash
curl "http://localhost:5000/api/grounds/search?location=Mumbai&sport_type=Football&max_price=100000"
```

### Sync Grounds
```bash
curl -X POST http://localhost:5000/api/sync-grounds
```

### Check if Server Running
```bash
curl http://localhost:5000/
# Should return HTML homepage
```

---

## 🌐 URL Structure

```
http://localhost:5000/
├── / (homepage)
├── /register (public)
├── /login (public)
├── /logout (protected)
├── /grounds (public)
├── /booking/<id> (protected)
├── /my-bookings (protected)
├── /cancel-booking/<id> (protected)
├── /payment/<id> (protected)
├── /payment/verify (protected, AJAX)
├── /payment/success/<id> (protected)
├── /payment/failed/<id> (protected)
├── /analytics (protected)
└── /api/
    ├── /grounds/search (public API)
    └── /sync-grounds (admin API)
```

---

## 💬 Common URL Patterns

### With Ground ID
- `/booking/1` - Book ground with ID 1
- `/ground/1/details` - Get ground details

### With Booking ID
- `/payment/42` - Pay for booking 42
- `/payment/success/42` - Confirm payment for booking 42
- `/cancel-booking/42` - Cancel booking 42

### Query Parameters
- `/api/grounds/search?location=Mumbai`
- `/api/grounds/search?location=Mumbai&sport_type=Football`
- `/api/grounds/search?max_price=100000`

---

## ✅ Verification Checklist

After running `python3 app.py`, verify:
- [ ] `http://localhost:5000/` loads (homepage)
- [ ] `http://localhost:5000/grounds` shows grounds
- [ ] `http://localhost:5000/register` loads registration
- [ ] `http://localhost:5000/login` loads login
- [ ] API: `http://localhost:5000/api/grounds/search?location=Mumbai` returns JSON

---

## 🐛 Troubleshooting URLs

### 404 - Page Not Found
- Check the URL path matches exactly
- Verify app is running on port 5000
- Check database has data (run seed_with_payments.py)

### 401 - Unauthorized (Redirects to Login)
- You're trying to access a protected route
- Login first at `/login`
- Create account at `/register` if needed

### 500 - Server Error
- Check console output for error message
- Check app.py has no syntax errors
- Restart app: `python3 app.py`

---

## 📱 Mobile URLs

All URLs work on mobile devices:
- Same URLs as desktop
- Responsive design adapts automatically
- Touch-friendly buttons and forms

---

## 🔐 Security Notes

1. **Never pass passwords in URL** - Use POST requests
2. **CSRF tokens required** for form submissions
3. **Session cookies** secure the user authentication
4. **HTTPS recommended** for production (update URLs to https://)

---

## 📊 Example API Responses

### Successful Search
```json
{
  "success": true,
  "grounds": [
    {
      "id": 1,
      "name": "SportZone Football Academy",
      "sport_type": "Football",
      "location": "Mumbai, Maharashtra",
      "price_per_hour": 800,
      "contact_phone": "9876543210",
      "amenities": "lights,parking,changing_room,cafeteria",
      "rating": 4.8
    }
  ]
}
```

### Successful Payment Verification
```json
{
  "success": true,
  "message": "Payment verified successfully",
  "booking_id": 42,
  "payment_id": "pay_123456"
}
```

### Failed Payment Verification
```json
{
  "success": false,
  "message": "Signature verification failed",
  "error": "Invalid signature"
}
```

---

## 🚀 Quick Reference

| Need | URL |
|------|-----|
| Home | `/` |
| Browse grounds | `/grounds` |
| Register | `/register` |
| Login | `/login` |
| My bookings | `/my-bookings` |
| Analytics | `/analytics` |
| API search | `/api/grounds/search?location=...` |
| API sync | `POST /api/sync-grounds` |

---

**Last Updated**: August 30, 2024
**Version**: 1.0.0
