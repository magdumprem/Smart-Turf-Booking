# TurfZone - Deployment Checklist & Troubleshooting

## 🚀 Pre-Launch Checklist

### Environment Setup
- [ ] Python 3.7+ installed
- [ ] Virtual environment created
- [ ] `.env` file created from `.env.example`
- [ ] All environment variables configured
- [ ] `requirements.txt` installed

### Database
- [ ] SQLite working (dev) or PostgreSQL configured (prod)
- [ ] `python3 seed_with_payments.py` executed successfully
- [ ] Database contains sample data and users
- [ ] Database file permissions set correctly

### Payment Integration
- [ ] Razorpay account created
- [ ] API keys obtained from dashboard
- [ ] Keys added to `.env` file
- [ ] Test payments working with test cards

### API Integration (Optional but Recommended)
- [ ] External API provider chosen (JustDial/Google Places)
- [ ] API keys obtained
- [ ] API endpoint tested externally
- [ ] `fetch_real_grounds_from_api()` updated with real endpoint

### Frontend Verification
- [ ] All templates render without errors
- [ ] Header/footer display correctly
- [ ] Payment pages load
- [ ] Forms submit successfully
- [ ] Responsive design tested on mobile

### Security Review
- [ ] No hardcoded secrets in code
- [ ] Environment variables used for sensitive data
- [ ] CSRF tokens present on forms
- [ ] Password hashing enabled
- [ ] DEBUG mode set to False in production

---

## ⚠️ Common Issues & Solutions

### Issue 1: "No module named 'flask'"

**Cause**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt
```

---

### Issue 2: "No such file or directory: '.env'"

**Cause**: Environment file not created

**Solution**:
```bash
cp .env.example .env
# Edit .env with your Razorpay keys
```

---

### Issue 3: "Razorpay key not found" or "RAZORPAY_KEY_ID is None"

**Cause**: Environment variables not loaded

**Solution**:
```bash
# Option 1: Check .env file exists and has values
cat .env

# Option 2: Export manually
export RAZORPAY_KEY_ID=rzp_test_xxxxx
export RAZORPAY_KEY_SECRET=xxx

# Option 3: Use python-dotenv
pip install python-dotenv
# Add to app.py:
from dotenv import load_dotenv
load_dotenv()
```

---

### Issue 4: "Port 5000 already in use"

**Cause**: Another application using port 5000

**Solution**:
```bash
# Option 1: Use different port
python3 app.py --port 5001

# Option 2: Kill process using port 5000
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Option 3: Find and stop the service
netstat -tlnp | grep 5000
```

---

### Issue 5: "TemplateNotFound: base.html"

**Cause**: Templates folder not in correct location

**Solution**:
```bash
# Verify structure:
ls -la smart_sports_booking/templates/

# Should show:
# base.html
# grounds.html
# payment.html
# ... etc

# Check working directory:
pwd  # Should be in smart_sports_booking folder
```

---

### Issue 6: "Database is locked"

**Cause**: Multiple processes accessing SQLite simultaneously

**Solution**:
```bash
# Option 1: Delete and reseed database
rm instance/sports_booking.db
python3 seed_with_payments.py

# Option 2: Use PostgreSQL for production
# (SQLite has concurrency limitations)
```

---

### Issue 7: "Payment verification failed"

**Cause**: Incorrect signature or wrong secret key

**Solution**:
```bash
# 1. Verify KEY_SECRET is correct
echo $RAZORPAY_KEY_SECRET

# 2. Check signature calculation order (Order ID | Payment ID)
# Correct order: "{order_id}|{payment_id}"

# 3. Use HMAC-SHA256 (not other hash algorithms)

# 4. For test mode: verify signature check is working
# (Should pass with test data)
```

---

### Issue 8: "No modules named 'flask_sqlalchemy'"

**Cause**: Wrong package name or version mismatch

**Solution**:
```bash
# Reinstall with exact versions
pip install --force-reinstall -r requirements.txt

# Or upgrade specific package
pip install --upgrade Flask-SQLAlchemy==3.0.5
```

---

### Issue 9: "Booking doesn't show payment status"

**Cause**: Database schema not updated or data not refreshed

**Solution**:
```bash
# Check database:
python3 << 'EOF'
from app import app, db, Booking
with app.app_context():
    bookings = Booking.query.all()
    for b in bookings:
        print(f"Booking {b.id}: payment_status={b.payment_status}")
EOF

# If empty, reseed:
python3 seed_with_payments.py

# If payment_status column missing:
rm instance/sports_booking.db
python3 seed_with_payments.py
```

---

### Issue 10: "CSRF token missing" or "CSRF validation failed"

**Cause**: CSRF token not included in form

**Solution**:
```html
<!-- Ensure all forms have CSRF token -->
<form method="POST">
    {{ csrf_token() }}
    <!-- form fields -->
</form>

<!-- Or add in base.html headers for AJAX -->
<script>
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
</script>
```

---

### Issue 11: "No such column: booking.payment_status"

**Cause**: Using old database schema

**Solution**:
```bash
# Delete old database and recreate with new schema
rm instance/sports_booking.db

# Restart app (creates new schema)
python3 app.py

# Or seed with data:
python3 seed_with_payments.py
```

---

### Issue 12: "External API not returning grounds"

**Cause**: API endpoint not implemented or returns empty

**Solution**:
```python
# In app.py, update fetch_real_grounds_from_api():
def fetch_real_grounds_from_api():
    # Replace mock data with real API call:
    try:
        response = requests.get(
            'https://api.justdial.com/grounds',
            params={
                'location': 'Mumbai',
                'sport_type': 'Football',
                'api_key': os.environ.get('JUSTDIAL_API_KEY')
            },
            timeout=5
        )
        if response.status_code == 200:
            return response.json()['grounds']
    except Exception as e:
        print(f"API Error: {e}")
    
    # Fallback to empty list
    return []
```

---

### Issue 13: "SSL Certificate Error" in production

**Cause**: HTTPS not properly configured

**Solution**:
```python
# In app.py for production:
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Use nginx with SSL certificate:
# nginx config should have:
listen 443 ssl;
ssl_certificate /path/to/cert.pem;
ssl_certificate_key /path/to/key.pem;
```

---

### Issue 14: "Payment page loads but payment button doesn't work"

**Cause**: Razorpay script not loading or key ID incorrect

**Solution**:
```html
<!-- In payment.html, verify: -->
<script src="https://checkout.razorpay.com/v1/checkout.js"></script>

<!-- And check key is correct: -->
<script>
var razorpayKeyId = "{{ razorpay_key_id }}";
console.log("Key ID:", razorpayKeyId);  // Should not be undefined
</script>

<!-- If undefined, check app.py render_template: -->
# app.py should have:
return render_template('payment.html', 
    razorpay_key_id=app.config['RAZORPAY_KEY_ID'],
    booking=booking,
    ...
)
```

---

### Issue 15: "Forms not submitting / No POST data received"

**Cause**: Form method or action missing

**Solution**:
```html
<!-- Ensure form has:
1. method="POST"
2. action="{% url_for('route_name') %}"
3. CSRF token if needed
-->
<form method="POST" action="{{ url_for('create_booking', ground_id=ground.id) }}">
    {{ csrf_token() }}
    <input type="text" name="booking_date" required>
    <input type="text" name="time_slot" required>
    <button type="submit">Book Now</button>
</form>
```

---

## 🧪 Testing Procedures

### Test 1: Complete Booking Flow
```bash
1. http://localhost:5000 → Homepage
2. Click "Browse Grounds" → /grounds
3. Click "Book Now" on any ground → /booking/<id>
4. Fill form and submit → Creates booking
5. Verify booking appears in "My Bookings"
```

### Test 2: Payment Flow
```bash
1. Go to "My Bookings" page
2. Find booking with "Pending Payment" status
3. Click "Pay Now" → /payment/<booking_id>
4. Click "Pay with Razorpay"
5. Use test card: 4111111111111111
6. Complete payment
7. Verify redirect to success page
8. Check booking status changed to "Completed"
```

### Test 3: API Endpoints
```bash
# Search grounds
curl "http://localhost:5000/api/grounds/search?location=Mumbai&sport_type=Football"

# Sync grounds (admin only)
curl -X POST http://localhost:5000/api/sync-grounds

# Response should be JSON with grounds data
```

### Test 4: Authentication
```bash
1. Logout (if logged in)
2. Try accessing /my-bookings → Should redirect to login
3. Register new account
4. Login with credentials
5. Verify booking dashboard loads
```

---

## 📊 Performance Optimization

### Database Optimization
```python
# Add indexes to frequently queried columns:
# In models:
class Booking(db.Model):
    __table_args__ = (
        db.Index('idx_user_date', 'user_id', 'booking_date'),
        db.Index('idx_ground_date', 'ground_id', 'booking_date'),
    )
```

### Caching
```python
# Add caching for API responses:
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/api/grounds/search')
@cache.cached(timeout=300)
def search_grounds():
    # Results cached for 5 minutes
    pass
```

### Database Connection
```python
# Production: Use connection pooling
from sqlalchemy.pool import QueuePool
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'poolclass': QueuePool,
    'pool_size': 10,
    'pool_recycle': 3600,
}
```

---

## 🔒 Security Hardening

### Before Production Deployment
```python
# In app.py:
app.config.update(
    DEBUG=False,  # ✓ MUST be False
    TESTING=False,
    SECRET_KEY=os.environ.get('SECRET_KEY'),  # ✓ From .env
    
    # HTTPS/SSL
    PREFERRED_URL_SCHEME='https',
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    
    # CSRF
    WTF_CSRF_ENABLED=True,
    
    # Session
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24),
)
```

### Firewall Rules
```bash
# Only allow HTTPS
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp   # For redirect
sudo ufw deny 5000/tcp  # Development port

# Block direct access to Flask app
```

---

## 📈 Monitoring Setup

### Application Logging
```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Application started")
```

### Payment Tracking
```python
# Log all payments for audit
logger.info(f"Payment initiated: booking_id={booking_id}, amount={amount}")
logger.info(f"Payment verified: payment_id={payment_id}, status={status}")
```

### Performance Monitoring
```bash
# Monitor response times
pip install flask-debugtoolbar

# Monitor database queries
pip install sqlalchemy-utils
```

---

## 🚀 Production Deployment Guide

### Step 1: Server Setup
```bash
# Ubuntu 22.04 server
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv postgresql -y

# Create deployment user
sudo useradd -m -s /bin/bash turfzone
sudo mkdir -p /var/www/turfzone
sudo chown turfzone:turfzone /var/www/turfzone
```

### Step 2: Clone and Setup
```bash
sudo -u turfzone git clone <repo-url> /var/www/turfzone
cd /var/www/turfzone
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Environment Configuration
```bash
# Create .env with production values
sudo -u turfzone cp .env.example /var/www/turfzone/.env
# Edit .env with production keys
```

### Step 4: Database Setup
```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE turfzone;
CREATE USER turfzone WITH PASSWORD 'secure_password';
ALTER ROLE turfzone SET client_encoding TO 'utf8';
ALTER ROLE turfzone SET default_transaction_isolation TO 'read committed';
ALTER ROLE turfzone SET default_transaction_deferrable TO on;
ALTER ROLE turfzone SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE turfzone TO turfzone;
```

### Step 5: Gunicorn Setup
```bash
# Install Gunicorn
pip install gunicorn

# Create systemd service
sudo tee /etc/systemd/system/turfzone.service > /dev/null <<EOF
[Unit]
Description=TurfZone Sports Booking
After=network.target

[Service]
User=turfzone
WorkingDirectory=/var/www/turfzone
Environment="PATH=/var/www/turfzone/venv/bin"
ExecStart=/var/www/turfzone/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start turfzone
sudo systemctl enable turfzone
```

### Step 6: Nginx Setup
```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx config
sudo tee /etc/nginx/sites-available/turfzone > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /static {
        alias /var/www/turfzone/static;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/turfzone /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 7: SSL Certificate
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot certonly --nginx -d your-domain.com
```

---

## 🎯 Troubleshooting Workflow

1. **Check Application Logs**
   ```bash
   tail -f app.log
   # or
   journalctl -u turfzone -f
   ```

2. **Check Database Status**
   ```bash
   psql -U turfzone -d turfzone -c "SELECT * FROM user;"
   ```

3. **Check Server Health**
   ```bash
   ps aux | grep gunicorn
   curl http://localhost:5000/
   ```

4. **Check Payment Logs**
   ```bash
   grep -i payment app.log
   ```

5. **Restart Application**
   ```bash
   sudo systemctl restart turfzone
   ```

---

## 📞 Support Contacts

- **Razorpay Support**: https://razorpay.com/support
- **Flask Documentation**: https://flask.palletsprojects.com
- **PostgreSQL Docs**: https://www.postgresql.org/docs
- **Nginx Docs**: https://nginx.org/en/docs/

---

**Last Updated**: August 30, 2024
**Version**: 1.0.0
