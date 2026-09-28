#!/bin/bash
# QUICKSTART.sh - Setup and run TurfZone application in 5 minutes

set -e

echo "🚀 TurfZone - Quick Start Script"
echo "================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✓ Python $(python3 --version | cut -d' ' -f2) detected"
echo ""

# Step 1: Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Step 2: Setup environment
echo "⚙️  Setting up environment..."
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your Razorpay keys:"
    echo "   1. Get keys from: https://dashboard.razorpay.com"
    echo "   2. Edit .env and add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET"
else
    echo "✓ .env file exists"
fi
echo ""

# Step 3: Seed database
echo "🌱 Seeding database with demo data..."
python3 seed_with_payments.py
echo ""

# Step 4: Print instructions
echo "================================="
echo "✅ Setup Complete!"
echo "================================="
echo ""
echo "📝 Next Steps:"
echo "1. Update .env with Razorpay keys (if not done)"
echo "2. Run: python3 app.py"
echo "3. Open: http://localhost:5000"
echo "4. Login with demo credentials (see seed output above)"
echo ""
echo "💳 Test Payments:"
echo "Card: 4111111111111111 | CVV: Any | Expiry: Any future date"
echo ""
echo "📚 Documentation:"
echo "- README.md - Project overview"
echo "- PAYMENT_AND_API_SETUP.md - Payment & API guide"
echo ""
