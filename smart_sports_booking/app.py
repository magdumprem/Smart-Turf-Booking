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

# Use Render environment variable if available
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "turfzone_secret_key_2026"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Use DATABASE_PATH on deployment.
# Otherwise use local SQLite database.
DATABASE = os.environ.get(
    "DATABASE_PATH",
    os.path.join(BASE_DIR, "turf_booking.db")
)


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

            FOREIGN KEY (user_id)
                REFERENCES users(id),

            FOREIGN KEY (turf_id)
                REFERENCES turfs(id)
        )
    """)


    # ========================================================
    # DATABASE MIGRATION
    #
    # If your old database already exists without
    # payment_status, add it automatically.
    # ========================================================

    try:

        conn.execute("""
            ALTER TABLE bookings
            ADD COLUMN payment_status TEXT DEFAULT 'Pending'
        """)

    except sqlite3.OperationalError:

        # Column already exists
        pass


    # ========================================================
    # OLD BOOKINGS MIGRATION
    #
    # Existing Confirmed bookings are treated as paid.
    # ========================================================

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
    # INSERT SAMPLE TURFS
    # ========================================================

    turf_count = conn.execute("""
        SELECT COUNT(*)
        FROM turfs
    """).fetchone()[0]


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
# INITIALIZE DATABASE
#
# IMPORTANT:
# This runs even when using:
# gunicorn app:app
# ============================================================

init_db()


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


# ============================================================
# CURRENT USER CONTEXT
# ============================================================

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
# HOME
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
# CREATE BOOKING
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
        # CHECK OVERLAPPING BOOKINGS
        #
        # Both Pending and Confirmed bookings block a slot.
        # Example:
        # Existing: 20:00 - 21:00
        # New:      20:30 - 21:30  -> BLOCKED
        # New:      21:00 - 22:00  -> ALLOWED
        # ====================================================

        def time_to_minutes(time_string):
            try:
                hours, minutes = map(int, time_string.split(":"))
                if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
                    return None
                return hours * 60 + minutes
            except (ValueError, AttributeError):
                return None

        requested_start = time_to_minutes(start_time)

        if requested_start is None:
            conn.close()
            flash(
                "Invalid start time. Please select a valid time.",
                "danger"
            )
            return redirect(
                url_for(
                    "create_booking",
                    ground_id=ground_id
                )
            )

        requested_end = requested_start + (duration * 60)

        if requested_end > 24 * 60:
            conn.close()
            flash(
                "Booking duration extends past midnight. Please choose an earlier start time.",
                "danger"
            )
            return redirect(
                url_for(
                    "create_booking",
                    ground_id=ground_id
                )
            )

        existing_bookings = conn.execute("""
            SELECT id, start_time, duration
            FROM bookings

            WHERE turf_id = ?

              AND booking_date = ?

              AND status IN (
                  'Pending',
                  'Confirmed'
              )

            ORDER BY start_time
        """, (
            ground_id,
            booking_date
        )).fetchall()

        overlapping_booking = None

        for existing in existing_bookings:
            existing_start = time_to_minutes(existing["start_time"])

            if existing_start is None:
                continue

            existing_end = existing_start + (int(existing["duration"]) * 60)

            # Two time ranges overlap when:
            # requested_start < existing_end
            # AND requested_end > existing_start
            if requested_start < existing_end and requested_end > existing_start:
                overlapping_booking = existing
                break

        if overlapping_booking:
            conn.close()

            flash(
                f"This turf is already booked from {overlapping_booking['start_time']} "
                f"for {overlapping_booking['duration']} hour(s). Please choose another time.",
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
            ground["price_per_hour"]
            * duration
        )


        # ====================================================
        # SAVE BOOKING
        #
        # Booking starts as Pending.
        # User must complete payment.
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
            "info"
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
    # ALREADY PAID
    # ========================================================

    if booking["payment_status"] == "Completed":

        conn.close()

        flash(
            "Payment has already been completed.",
            "info"
        )

        return redirect(
            url_for(
                "payment_success",
                booking_id=booking_id
            )
        )


    # ========================================================
    # CANCELLED BOOKING
    # ========================================================

    if booking["status"] == "Cancelled":

        conn.close()

        flash(
            "Cancelled bookings cannot be paid for.",
            "danger"
        )

        return redirect(
            url_for("my_bookings")
        )


    # ========================================================
    # PAYMENT SUBMISSION
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


        # ====================================================
        # DEMO PAYMENT
        #
        # No real money is processed.
        # ====================================================

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


        flash(
            "Payment completed successfully!",
            "success"
        )


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

          AND status IN (
              'Pending',
              'Confirmed'
          )

        ORDER BY start_time
    """, (
        turf_id,
        booking_date
    )).fetchall()


    def time_to_minutes(time_string):
        try:
            hours, minutes = map(int, time_string.split(":"))
            return hours * 60 + minutes
        except (ValueError, AttributeError):
            return None


    def minutes_to_time(total_minutes):
        total_minutes = total_minutes % (24 * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"


    booked_slots = []

    for booking in bookings:
        start_minutes = time_to_minutes(booking["start_time"])

        if start_minutes is None:
            continue

        end_minutes = start_minutes + (int(booking["duration"]) * 60)

        booked_slots.append({
            "start_time": booking["start_time"],
            "end_time": minutes_to_time(end_minutes),
            "duration": int(booking["duration"])
        })


    conn.close()


    return jsonify({
        "success": True,

        "bookings": [
            dict(booking)
            for booking in bookings
        ],

        "booked_slots": booked_slots
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

    try:

        conn = get_db()

        conn.execute(
            "SELECT 1"
        )

        conn.close()


        return jsonify({
            "status": "healthy",
            "application": "TurfZone",
            "database": "connected"
        })


    except Exception as e:

        return jsonify({
            "status": "unhealthy",
            "application": "TurfZone",
            "database": "error",
            "message": str(e)
        }), 500


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "TURFZONE - SMART TURF BOOKING SYSTEM"
    )

    print("=" * 60)

    print(
        f"Database: {DATABASE}"
    )

    print(
        "Server starting..."
    )

    print("=" * 60)


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )