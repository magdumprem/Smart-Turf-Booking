from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify
)
import sqlite3
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

app.secret_key = "turfzone_secret_key_2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "turf_booking.db")


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():

    conn = get_db()

    # ========================================================
    # USERS TABLE
    # ========================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ========================================================
    # TURFS TABLE
    # ========================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS turfs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            sport_type TEXT NOT NULL,
            price_per_hour REAL NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ========================================================
    # BOOKINGS TABLE
    # ========================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            turf_id INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            duration INTEGER NOT NULL,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            payment_status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (turf_id) REFERENCES turfs(id)
        )
    """)

    # ========================================================
    # DATABASE MIGRATION
    # ========================================================
    # Your existing database was created without payment_status.
    # This adds the column without deleting your existing data.

    try:

        conn.execute("""
            ALTER TABLE bookings
            ADD COLUMN payment_status TEXT DEFAULT 'Pending'
        """)

    except sqlite3.OperationalError:

        # Column already exists
        pass

    # ========================================================
    # OLD CONFIRMED BOOKINGS
    # ========================================================
    # Old bookings were automatically confirmed before payment
    # was added. Treat those as already paid.

    conn.execute("""
        UPDATE bookings
        SET payment_status = 'Completed'
        WHERE status = 'Confirmed'
          AND (
              payment_status IS NULL
              OR payment_status = 'Pending'
          )
    """)

    # ========================================================
    # INSERT SAMPLE TURFS IF DATABASE IS EMPTY
    # ========================================================

    turf_count = conn.execute(
        "SELECT COUNT(*) FROM turfs"
    ).fetchone()[0]

    if turf_count == 0:

        sample_turfs = [

            (
                "Kolhapur Football Arena",
                "Kolhapur",
                "Football",
                800,
                "Premium football turf with professional lighting."
            ),

            (
                "Champions Cricket Turf",
                "Kolhapur",
                "Cricket",
                1000,
                "Spacious cricket turf suitable for practice and matches."
            ),

            (
                "Smash Badminton Arena",
                "Kolhapur",
                "Badminton",
                500,
                "Indoor badminton courts with quality flooring."
            ),

            (
                "Ace Tennis Court",
                "Kolhapur",
                "Tennis",
                700,
                "Professional tennis court for singles and doubles."
            ),

            (
                "Elite Basketball Court",
                "Kolhapur",
                "Basketball",
                600,
                "Modern basketball court for training and matches."
            ),

            (
                "Victory Volleyball Arena",
                "Kolhapur",
                "Volleyball",
                550,
                "Well-maintained volleyball court."
            )
        ]

        conn.executemany("""
            INSERT INTO turfs
            (
                name,
                location,
                sport_type,
                price_per_hour,
                description
            )
            VALUES (?, ?, ?, ?, ?)
        """, sample_turfs)

    conn.commit()
    conn.close()


# ============================================================
# CURRENT USER
# ============================================================

class CurrentUser:

    def __init__(self, user=None):
        self.user = user

    @property
    def is_authenticated(self):
        return self.user is not None

    @property
    def id(self):
        return self.user["id"] if self.user else None

    @property
    def username(self):
        return self.user["username"] if self.user else None

    @property
    def email(self):
        return self.user["email"] if self.user else None


@app.context_processor
def inject_current_user():

    user = None

    if "user_id" in session:

        conn = get_db()

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE id = ?
        """, (
            session["user_id"],
        )).fetchone()

        conn.close()

    return {
        "current_user": CurrentUser(user)
    }


# ============================================================
# LOGIN REQUIRED DECORATOR
# ============================================================

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login first.",
                "warning"
            )

            return redirect(
                url_for("login")
            )

        return f(*args, **kwargs)

    return decorated_function


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return redirect(
        url_for("ground_list")
    )


# ============================================================
# BROWSE GROUNDS
# ============================================================

@app.route("/grounds")
def ground_list():

    conn = get_db()

    grounds = conn.execute("""
        SELECT *
        FROM turfs
        ORDER BY id ASC
    """).fetchall()

    conn.close()

    return render_template(
        "grounds.html",
        grounds=grounds
    )


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        if not username or not email or not password:

            flash(
                "Username, email and password are required.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        conn = get_db()

        existing_user = conn.execute("""
            SELECT id
            FROM users
            WHERE email = ?
        """, (
            email,
        )).fetchone()

        if existing_user:

            conn.close()

            flash(
                "An account with this email already exists.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        hashed_password = generate_password_hash(
            password
        )

        conn.execute("""
            INSERT INTO users
            (
                username,
                email,
                password,
                phone
            )
            VALUES (?, ?, ?, ?)
        """, (
            username,
            email,
            hashed_password,
            phone
        ))

        conn.commit()
        conn.close()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        ).strip()

        conn = get_db()

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (
            email,
        )).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]

            flash(
                f"Welcome back, {user['username']}!",
                "success"
            )

            return redirect(
                url_for("ground_list")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("ground_list")
    )


# ============================================================
# BOOKING PAGE
# ============================================================

@app.route(
    "/booking/<int:ground_id>",
    methods=["GET", "POST"]
)
@login_required
def create_booking(ground_id):

    conn = get_db()

    ground = conn.execute("""
        SELECT *
        FROM turfs
        WHERE id = ?
    """, (
        ground_id,
    )).fetchone()

    if not ground:

        conn.close()

        flash(
            "Turf not found.",
            "danger"
        )

        return redirect(
            url_for("ground_list")
        )

    # ========================================================
    # CREATE BOOKING
    # ========================================================

    if request.method == "POST":

        booking_date = request.form.get(
            "booking_date",
            ""
        ).strip()

        start_time = request.form.get(
            "start_time",
            ""
        ).strip()

        duration = request.form.get(
            "duration",
            "1"
        ).strip()

        try:

            duration = int(duration)

        except ValueError:

            duration = 1

        if duration < 1:

            duration = 1

        if not booking_date or not start_time:

            conn.close()

            flash(
                "Please select date and time.",
                "danger"
            )

            return redirect(
                url_for(
                    "create_booking",
                    ground_id=ground_id
                )
            )

        # ====================================================
        # CHECK DUPLICATE BOOKING
        # ====================================================
        # Both Pending and Confirmed bookings occupy the slot.

        existing_booking = conn.execute("""
            SELECT id
            FROM bookings
            WHERE turf_id = ?
              AND booking_date = ?
              AND start_time = ?
              AND status IN ('Pending', 'Confirmed')
        """, (
            ground_id,
            booking_date,
            start_time
        )).fetchone()

        if existing_booking:

            conn.close()

            flash(
                "This time slot is already booked or awaiting payment.",
                "danger"
            )

            return redirect(
                url_for(
                    "create_booking",
                    ground_id=ground_id
                )
            )

        # ====================================================
        # CALCULATE TOTAL PRICE
        # ====================================================

        total_price = (
            ground["price_per_hour"] * duration
        )

        # ====================================================
        # SAVE BOOKING
        # ====================================================

        conn.execute("""
            INSERT INTO bookings
            (
                user_id,
                turf_id,
                booking_date,
                start_time,
                duration,
                total_price,
                status,
                payment_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            ground_id,
            booking_date,
            start_time,
            duration,
            total_price,
            "Pending",
            "Pending"
        ))

        conn.commit()

        conn.close()

        flash(
            "Booking created successfully. Please complete payment.",
            "success"
        )

        return redirect(
            url_for("my_bookings")
        )

    conn.close()

    return render_template(
        "booking.html",
        ground=ground
    )


# ============================================================
# MY BOOKINGS
# ============================================================

@app.route("/my-bookings")
@login_required
def my_bookings():

    conn = get_db()

    bookings = conn.execute("""
        SELECT
            bookings.*,
            turfs.name AS turf_name,
            turfs.location,
            turfs.sport_type
        FROM bookings
        JOIN turfs
            ON bookings.turf_id = turfs.id
        WHERE bookings.user_id = ?
        ORDER BY
            bookings.booking_date DESC,
            bookings.start_time DESC
    """, (
        session["user_id"],
    )).fetchall()

    conn.close()

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )


# ============================================================
# CANCEL BOOKING
# ============================================================

@app.route(
    "/booking/cancel/<int:booking_id>",
    methods=["POST"]
)
@login_required
def cancel_booking(booking_id):

    conn = get_db()

    booking = conn.execute("""
        SELECT *
        FROM bookings
        WHERE id = ?
          AND user_id = ?
    """, (
        booking_id,
        session["user_id"]
    )).fetchone()

    if not booking:

        conn.close()

        flash(
            "Booking not found.",
            "danger"
        )

        return redirect(
            url_for("my_bookings")
        )

    if booking["status"] == "Cancelled":

        conn.close()

        flash(
            "This booking is already cancelled.",
            "warning"
        )

        return redirect(
            url_for("my_bookings")
        )

    conn.execute("""
        UPDATE bookings
        SET status = 'Cancelled'
        WHERE id = ?
          AND user_id = ?
    """, (
        booking_id,
        session["user_id"]
    ))

    conn.commit()
    conn.close()

    flash(
        "Booking cancelled successfully.",
        "success"
    )

    return redirect(
        url_for("my_bookings")
    )


# ============================================================
# PAYMENT PAGE
# ============================================================

@app.route(
    "/payment/<int:booking_id>",
    methods=["GET", "POST"]
)
@login_required
def initiate_payment(booking_id):

    conn = get_db()

    booking = conn.execute("""
        SELECT
            bookings.*,
            turfs.name AS turf_name,
            turfs.location,
            turfs.sport_type
        FROM bookings
        JOIN turfs
            ON bookings.turf_id = turfs.id
        WHERE bookings.id = ?
          AND bookings.user_id = ?
    """, (
        booking_id,
        session["user_id"]
    )).fetchone()

    if not booking:

        conn.close()

        flash(
            "Booking not found.",
            "danger"
        )

        return redirect(
            url_for("my_bookings")
        )

    # ========================================================
    # CHECK IF ALREADY PAID
    # ========================================================

    if booking["payment_status"] == "Completed":

        conn.close()

        flash(
            "Payment for this booking is already completed.",
            "info"
        )

        return redirect(
            url_for(
                "payment_success",
                booking_id=booking_id
            )
        )

    # ========================================================
    # CHECK CANCELLED BOOKING
    # ========================================================

    if booking["status"] == "Cancelled":

        conn.close()

        flash(
            "Cancelled bookings cannot be paid.",
            "danger"
        )

        return redirect(
            url_for("my_bookings")
        )

    # ========================================================
    # PROCESS PAYMENT
    # ========================================================

    if request.method == "POST":

        payment_method = request.form.get(
            "payment_method",
            ""
        ).strip()

        if not payment_method:

            conn.close()

            flash(
                "Please select a payment method.",
                "danger"
            )

            return redirect(
                url_for(
                    "initiate_payment",
                    booking_id=booking_id
                )
            )

        # ----------------------------------------------------
        # SIMULATED PAYMENT
        # ----------------------------------------------------
        # This is a demo payment system for the mini project.
        # No real money is transferred.

        conn.execute("""
            UPDATE bookings
            SET
                payment_status = 'Completed',
                status = 'Confirmed'
            WHERE id = ?
              AND user_id = ?
        """, (
            booking_id,
            session["user_id"]
        ))

        conn.commit()
        conn.close()

        return redirect(
            url_for(
                "payment_success",
                booking_id=booking_id
            )
        )

    conn.close()

    return render_template(
        "payment.html",
        booking=booking
    )


# ============================================================
# PAYMENT SUCCESS
# ============================================================

@app.route(
    "/payment/success/<int:booking_id>"
)
@login_required
def payment_success(booking_id):

    conn = get_db()

    booking = conn.execute("""
        SELECT
            bookings.*,
            turfs.name AS turf_name,
            turfs.location,
            turfs.sport_type
        FROM bookings
        JOIN turfs
            ON bookings.turf_id = turfs.id
        WHERE bookings.id = ?
          AND bookings.user_id = ?
    """, (
        booking_id,
        session["user_id"]
    )).fetchone()

    conn.close()

    if not booking:

        flash(
            "Booking not found.",
            "danger"
        )

        return redirect(
            url_for("my_bookings")
        )

    return render_template(
        "payment_success.html",
        booking=booking
    )


# ============================================================
# API - ALL TURFS
# ============================================================

@app.route("/api/turfs")
def api_turfs():

    conn = get_db()

    turfs = conn.execute("""
        SELECT *
        FROM turfs
        ORDER BY id
    """).fetchall()

    conn.close()

    return jsonify([
        dict(turf)
        for turf in turfs
    ])


# ============================================================
# API - SINGLE TURF
# ============================================================

@app.route(
    "/api/turfs/<int:turf_id>"
)
def api_single_turf(turf_id):

    conn = get_db()

    turf = conn.execute("""
        SELECT *
        FROM turfs
        WHERE id = ?
    """, (
        turf_id,
    )).fetchone()

    conn.close()

    if not turf:

        return jsonify({
            "success": False,
            "message": "Turf not found"
        }), 404

    return jsonify({
        "success": True,
        "turf": dict(turf)
    })


# ============================================================
# API - CHECK AVAILABILITY
# ============================================================

@app.route("/api/availability")
def api_availability():

    turf_id = request.args.get(
        "turf_id"
    )

    booking_date = request.args.get(
        "date"
    )

    if not turf_id or not booking_date:

        return jsonify({
            "success": False,
            "message": "turf_id and date are required"
        }), 400

    conn = get_db()

    bookings = conn.execute("""
        SELECT
            start_time,
            duration
        FROM bookings
        WHERE turf_id = ?
          AND booking_date = ?
          AND status IN ('Pending', 'Confirmed')
        ORDER BY start_time
    """, (
        turf_id,
        booking_date
    )).fetchall()

    conn.close()

    return jsonify({
        "success": True,
        "bookings": [
            dict(booking)
            for booking in bookings
        ]
    })


# ============================================================
# API - REGISTER
# ============================================================

@app.route(
    "/api/register",
    methods=["POST"]
)
def api_register():

    data = request.get_json(
        silent=True
    ) or {}

    username = data.get(
        "username",
        ""
    ).strip()

    email = data.get(
        "email",
        ""
    ).strip().lower()

    password = data.get(
        "password",
        ""
    ).strip()

    phone = data.get(
        "phone",
        ""
    ).strip()

    if not username or not email or not password:

        return jsonify({
            "success": False,
            "message": "Username, email and password are required."
        }), 400

    conn = get_db()

    existing = conn.execute("""
        SELECT id
        FROM users
        WHERE email = ?
    """, (
        email,
    )).fetchone()

    if existing:

        conn.close()

        return jsonify({
            "success": False,
            "message": "Email already registered."
        }), 409

    hashed_password = generate_password_hash(
        password
    )

    cursor = conn.execute("""
        INSERT INTO users
        (
            username,
            email,
            password,
            phone
        )
        VALUES (?, ?, ?, ?)
    """, (
        username,
        email,
        hashed_password,
        phone
    ))

    conn.commit()

    user_id = cursor.lastrowid

    conn.close()

    return jsonify({
        "success": True,
        "message": "Registration successful.",
        "user_id": user_id
    }), 201


# ============================================================
# API - LOGIN
# ============================================================

@app.route(
    "/api/login",
    methods=["POST"]
)
def api_login():

    data = request.get_json(
        silent=True
    ) or {}

    email = data.get(
        "email",
        ""
    ).strip().lower()

    password = data.get(
        "password",
        ""
    ).strip()

    conn = get_db()

    user = conn.execute("""
        SELECT *
        FROM users
        WHERE email = ?
    """, (
        email,
    )).fetchone()

    conn.close()

    if not user or not check_password_hash(
        user["password"],
        password
    ):

        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    session["user_id"] = user["id"]

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "healthy",
        "application": "TurfZone",
        "database": "connected"
    })


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    init_db()

    print("=" * 60)
    print("TURFZONE - SMART TURF BOOKING SYSTEM")
    print("=" * 60)
    print(f"Database: {DATABASE}")
    print("Server starting...")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )