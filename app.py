from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import re
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-before-production"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "seva_mithra.db")


# ============================================================
# SERVICES
# ============================================================

SERVICES = [
    ("⚡", "Electrician", "Wiring, fans & repairs"),
    ("🔧", "Plumber", "Leaks, taps & pipes"),
    ("🧹", "Cleaning", "Home & deep cleaning"),
    ("❄️", "AC Repair", "Service & installation"),
    ("🪚", "Carpenter", "Furniture & woodwork"),
    ("🎨", "Painting", "Interior & exterior"),
    ("🔌", "Appliance Repair", "TV, fridge & more"),
    ("👨‍🏫", "Tutor", "School, college & online"),
    ("💇", "Beauty Services", "Beauty at home"),
    ("🛠️", "Other Services", "Find more professionals"),
]

SERVICE_NAMES = [item[1] for item in SERVICES]

SERVICE_CATALOG = {
    "Electrician": [
        "Fan Installation", "Switch & Socket Repair", "Light Installation",
        "Wiring & Rewiring", "MCB / Fuse Repair", "Inverter Installation",
        "Doorbell Installation", "Power Point Installation",
        "Electrical Inspection", "Short Circuit Repair"
    ],
    "Plumber": [
        "Tap Repair", "Pipe Leakage Repair", "Wash Basin Installation",
        "Toilet Repair", "Water Tank Service", "Drain Cleaning",
        "Shower Installation", "Kitchen Sink Repair", "Bathroom Plumbing",
        "Water Motor Repair"
    ],
    "Cleaning": [
        "Full Home Cleaning", "Deep Cleaning", "Kitchen Cleaning",
        "Bathroom Cleaning", "Sofa Cleaning", "Carpet Cleaning",
        "Window Cleaning", "Move-in Cleaning", "Move-out Cleaning",
        "Office Cleaning"
    ],
    "AC Repair": [
        "AC General Service", "AC Gas Filling", "AC Installation",
        "AC Uninstallation", "AC Cooling Repair", "Water Leakage Repair",
        "AC PCB Repair", "AC Compressor Check", "AC Filter Cleaning",
        "AC Annual Service"
    ],
    "Carpenter": [
        "Furniture Repair", "Door Repair", "Door Installation",
        "Wardrobe Repair", "Table Repair", "Chair Repair",
        "Shelf Installation", "Curtain Rod Installation", "Bed Repair",
        "Custom Woodwork"
    ],
    "Painting": [
        "Room Painting", "Full Home Painting", "Exterior Painting",
        "Wall Texture", "Ceiling Painting", "Door Painting",
        "Metal Painting", "Waterproof Painting", "Office Painting",
        "Color Consultation"
    ],
    "Appliance Repair": [
        "Refrigerator Repair", "Washing Machine Repair",
        "Microwave Repair", "TV Repair", "Water Purifier Repair",
        "Geyser Repair", "Chimney Repair", "Mixer Grinder Repair",
        "Dishwasher Repair", "Air Cooler Repair"
    ],
    "Tutor": [
        "School Tuition", "Mathematics", "Science", "Computer / Programming",
        "English", "Other Languages", "College Subjects",
        "Competitive Exam Preparation", "Home Tutor", "Online Tutor"
    ],
    "Beauty Services": [
        "Haircut at Home", "Hair Styling", "Facial", "Manicure",
        "Pedicure", "Threading", "Waxing", "Makeup", "Hair Spa",
        "Bridal / Event Makeup"
    ],
    "Other Services": [
        "Pest Control", "Gardening", "Packers & Movers Help",
        "Laundry Service", "Car Wash", "CCTV Installation",
        "Wi-Fi / Router Setup", "Computer Repair", "Mobile Repair",
        "General Handyman"
    ],
}

TUTOR_TYPES = SERVICE_CATALOG["Tutor"]


# ============================================================
# DUMMY PROVIDERS - 3 FOR EACH SERVICE
# ============================================================

DUMMY_PROVIDERS = {
    "Electrician": [
        ("Arjun Electricals", "9876501001", "Repair & Installation", "8 years",
         "ITI Electrical", "Hyderabad", "₹299 onwards"),
        ("PowerFix Solutions", "9876501002", "Home Wiring & Repairs", "5 years",
         "Diploma Electrical", "Hyderabad", "₹349 onwards"),
        ("BrightWire Services", "9876501003", "Installation & Inspection", "11 years",
         "ITI + Safety Certified", "Hyderabad", "₹499 onwards"),
    ],
    "Plumber": [
        ("Sai Plumbing Works", "9876501101", "Bathroom & Kitchen Plumbing", "7 years",
         "ITI Plumbing", "Hyderabad", "₹249 onwards"),
        ("AquaFix Experts", "9876501102", "Leakage & Pipe Repair", "4 years",
         "Plumbing Certificate", "Hyderabad", "₹299 onwards"),
        ("FlowPro Services", "9876501103", "Water Tank & Motor Service", "10 years",
         "ITI Plumbing", "Hyderabad", "₹399 onwards"),
    ],
    "Cleaning": [
        ("CleanNest Services", "9876501201", "Home & Deep Cleaning", "6 years",
         "Professional Cleaning Certified", "Hyderabad", "₹499 onwards"),
        ("SparkleCare", "9876501202", "Kitchen & Bathroom Cleaning", "3 years",
         "Cleaning Specialist", "Hyderabad", "₹399 onwards"),
        ("FreshHome Experts", "9876501203", "Full Home & Office Cleaning", "9 years",
         "Facility Management", "Hyderabad", "₹699 onwards"),
    ],
    "AC Repair": [
        ("CoolCare AC", "9876501301", "AC Repair & Gas Filling", "9 years",
         "ITI Refrigeration", "Hyderabad", "₹399 onwards"),
        ("ChillTech Services", "9876501302", "Installation & Maintenance", "5 years",
         "Diploma HVAC", "Hyderabad", "₹449 onwards"),
        ("AirPro Experts", "9876501303", "PCB & Compressor Repair", "12 years",
         "HVAC Certified", "Hyderabad", "₹599 onwards"),
    ],
    "Carpenter": [
        ("WoodCraft Works", "9876501401", "Furniture Repair", "8 years",
         "ITI Carpenter", "Hyderabad", "₹349 onwards"),
        ("HomeWood Experts", "9876501402", "Doors & Wardrobes", "5 years",
         "Carpentry Certified", "Hyderabad", "₹399 onwards"),
        ("FineWood Studio", "9876501403", "Custom Woodwork", "13 years",
         "Master Carpenter", "Hyderabad", "₹699 onwards"),
    ],
    "Painting": [
        ("ColorNest Painters", "9876501501", "Interior Painting", "6 years",
         "Painting Specialist", "Hyderabad", "₹1,499/room"),
        ("PerfectCoat Services", "9876501502", "Exterior & Waterproof Painting", "9 years",
         "Certified Painter", "Hyderabad", "₹2,499/room"),
        ("BrushPro Experts", "9876501503", "Texture & Premium Painting", "12 years",
         "Advanced Painting Certified", "Hyderabad", "₹3,499/room"),
    ],
    "Appliance Repair": [
        ("QuickFix Appliances", "9876501601", "Refrigerator & Washing Machine", "7 years",
         "ITI Electronics", "Hyderabad", "₹299 onwards"),
        ("HomeTech Repairs", "9876501602", "TV & Microwave Repair", "4 years",
         "Diploma Electronics", "Hyderabad", "₹249 onwards"),
        ("ApplianceCare Pro", "9876501603", "Geyser & Water Purifier", "10 years",
         "Electronics Certified", "Hyderabad", "₹399 onwards"),
    ],
    "Tutor": [
        ("Anjali Sharma", "9876501701", "Mathematics & Science", "6 years",
         "M.Sc + B.Ed", "Hyderabad", "₹450/hour"),
        ("Rahul Verma", "9876501702", "Computer / Programming", "4 years",
         "M.Tech CSE", "Hyderabad", "₹600/hour"),
        ("Priya Reddy", "9876501703", "English & School Tuition", "9 years",
         "M.A + B.Ed", "Hyderabad", "₹400/hour"),
    ],
    "Beauty Services": [
        ("GlowAtHome", "9876501801", "Facial & Skin Care", "6 years",
         "Beauty Academy Certified", "Hyderabad", "₹599 onwards"),
        ("StylePro Beauty", "9876501802", "Hair Styling & Makeup", "4 years",
         "Professional Makeup Artist", "Hyderabad", "₹799 onwards"),
        ("BlushBeauty Experts", "9876501803", "Bridal & Event Makeup", "10 years",
         "Advanced Beauty Certified", "Hyderabad", "₹1,499 onwards"),
    ],
    "Other Services": [
        ("HomeAssist Services", "9876501901", "General Handyman", "7 years",
         "Multi-skill Certified", "Hyderabad", "₹299 onwards"),
        ("FixMate Solutions", "9876501902", "CCTV & Wi-Fi Setup", "5 years",
         "Diploma Electronics", "Hyderabad", "₹399 onwards"),
        ("CarePlus Services", "9876501903", "Gardening & Pest Control", "8 years",
         "Service Professional Certified", "Hyderabad", "₹499 onwards"),
    ],
}


# ============================================================
# DATABASE
# ============================================================

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB)

    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        password TEXT NOT NULL,
        address TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS providers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        password TEXT NOT NULL,
        service TEXT NOT NULL,
        work_type TEXT,
        experience TEXT,
        qualification TEXT,
        location TEXT,
        pricing TEXT,
        contact TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        provider_id INTEGER,
        service TEXT NOT NULL,
        work_type TEXT,
        address TEXT,
        booking_date TEXT,
        status TEXT NOT NULL DEFAULT 'Pending',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        provider_id INTEGER,
        rating INTEGER NOT NULL,
        review TEXT,
        created_at TEXT NOT NULL
    );
    """)

    cur = db.cursor()

    # Demo user
    if not cur.execute(
        "SELECT 1 FROM users WHERE email=?",
        ("user@demo.com",)
    ).fetchone():
        cur.execute(
            """
            INSERT INTO users
            (name,email,phone,password,address,created_at)
            VALUES(?,?,?,?,?,?)
            """,
            (
                "Demo User",
                "user@demo.com",
                "9876543210",
                generate_password_hash("123456"),
                "Hyderabad",
                datetime.now().isoformat(),
            ),
        )

    # Demo provider
    if not cur.execute(
        "SELECT 1 FROM providers WHERE email=?",
        ("provider@demo.com",)
    ).fetchone():
        cur.execute(
            """
            INSERT INTO providers
            (name,email,phone,password,service,work_type,
             experience,qualification,location,pricing,contact,created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                "Raj Kumar",
                "provider@demo.com",
                "9876543210",
                generate_password_hash("123456"),
                "Electrician",
                "Repair & Installation",
                "7 years",
                "ITI Electrical",
                "Hyderabad",
                "₹299 onwards",
                "9876543210",
                datetime.now().isoformat(),
            ),
        )

    # Dummy providers
    for service, provider_list in DUMMY_PROVIDERS.items():
        for (
            name, phone, work_type, experience,
            qualification, location, pricing
        ) in provider_list:

            email = (
                "demo."
                + re.sub(r"[^a-z0-9]+", "", name.lower())
                + "@sevamithra.demo"
            )

            if not cur.execute(
                "SELECT 1 FROM providers WHERE email=?",
                (email,),
            ).fetchone():
                cur.execute(
                    """
                    INSERT INTO providers
                    (name,email,phone,password,service,work_type,
                     experience,qualification,location,pricing,contact,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        name,
                        email,
                        phone,
                        generate_password_hash("123456"),
                        service,
                        work_type,
                        experience,
                        qualification,
                        location,
                        pricing,
                        phone,
                        datetime.now().isoformat(),
                    ),
                )

    db.commit()
    db.close()


init_db()


# ============================================================
# AUTH HELPERS
# ============================================================

def login_required(role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not session.get("logged_in"):
                flash("Please login first.")
                return redirect(url_for("login"))

            if role and session.get("role") != role:
                flash("You do not have permission to open that page.")
                return redirect(url_for("home"))

            return fn(*args, **kwargs)
        return wrapper
    return decorator


@app.context_processor
def global_data():
    return {"app_name": "Seva Mithra"}


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    db = get_db()
    providers = db.execute(
        "SELECT * FROM providers ORDER BY id DESC LIMIT 6"
    ).fetchall()

    return render_template(
        "index.html",
        services=SERVICES,
        providers=providers,
    )


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
@app.route("/register/<role>", methods=["GET", "POST"])
def register(role="user"):
    if role not in ("user", "provider"):
        role = "user"

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get(
            "confirm_password",
            request.form.get("confirm", ""),
        )

        if not all([name, email, phone, password]):
            flash("Please fill all required fields.")
            return render_template(
                "register.html",
                role=role,
                services=SERVICE_NAMES,
                tutor_types=TUTOR_TYPES,
            )

        if password != confirm:
            flash("Passwords do not match.")
            return render_template(
                "register.html",
                role=role,
                services=SERVICE_NAMES,
                tutor_types=TUTOR_TYPES,
            )

        db = get_db()

        try:
            if role == "user":
                db.execute(
                    """
                    INSERT INTO users
                    (name,email,phone,password,address,created_at)
                    VALUES(?,?,?,?,?,?)
                    """,
                    (
                        name,
                        email,
                        phone,
                        generate_password_hash(password),
                        request.form.get("address", "").strip(),
                        datetime.now().isoformat(),
                    ),
                )
            else:
                service = request.form.get(
                    "service",
                    request.form.get("category", "Other Services"),
                )

                if service not in SERVICE_NAMES:
                    service = "Other Services"

                db.execute(
                    """
                    INSERT INTO providers
                    (name,email,phone,password,service,work_type,
                     experience,qualification,location,pricing,contact,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        name,
                        email,
                        phone,
                        generate_password_hash(password),
                        service,
                        request.form.get("work_type", ""),
                        request.form.get("experience", ""),
                        request.form.get("qualification", ""),
                        request.form.get("location", ""),
                        request.form.get("pricing", ""),
                        phone,
                        datetime.now().isoformat(),
                    ),
                )

            db.commit()

        except sqlite3.IntegrityError:
            flash("An account with this email already exists.")
            return render_template(
                "register.html",
                role=role,
                services=SERVICE_NAMES,
                tutor_types=TUTOR_TYPES,
            )

        flash("Registration successful. Please login.")
        return redirect(url_for("login", role=role))

    return render_template(
        "register.html",
        role=role,
        services=SERVICE_NAMES,
        tutor_types=TUTOR_TYPES,
    )


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    selected_role = request.args.get("role", "user")

    if selected_role not in ("user", "provider", "admin"):
        selected_role = "user"

    if request.method == "POST":
        role = request.form.get("role", "user")
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if role not in ("user", "provider", "admin"):
            role = "user"

        db = get_db()

        # ====================================================
        # ADMIN LOGIN
        # ONLY THESE THREE ACCOUNTS ARE ADMINS
        # ====================================================
        if role == "admin":
            admin_credentials = {
                "sriram@gmail.com": "12345",
                "rahul@gmail.com": "5553",
                "vardhan@gmail.com": "6300",
            }

            if admin_credentials.get(email) == password:
                session.clear()
                session.update(
                    logged_in=True,
                    role="admin",
                    user_id=0,
                    name="Administrator",
                )
                return redirect(url_for("admin_dashboard"))

            flash("Invalid admin credentials.")
            return render_template(
                "login.html",
                selected_role="admin",
            )

        # ====================================================
        # SERVICE PROVIDER LOGIN
        # ====================================================
        if role == "provider":
            row = db.execute(
                "SELECT * FROM providers WHERE email=?",
                (email,),
            ).fetchone()

            if row and check_password_hash(row["password"], password):
                session.clear()
                session.update(
                    logged_in=True,
                    role="provider",
                    user_id=row["id"],
                    name=row["name"],
                )
                return redirect(url_for("provider_dashboard"))

            flash("Invalid provider email or password.")
            return render_template(
                "login.html",
                selected_role="provider",
            )

        # ====================================================
        # USER LOGIN
        # ====================================================
        row = db.execute(
            "SELECT * FROM users WHERE email=?",
            (email,),
        ).fetchone()

        if row and check_password_hash(row["password"], password):
            session.clear()
            session.update(
                logged_in=True,
                role="user",
                user_id=row["id"],
                name=row["name"],
            )
            return redirect(url_for("user_dashboard"))

        flash("Invalid user email or password.")

    return render_template(
        "login.html",
        selected_role=selected_role,
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("home"))


# ============================================================
# USER DASHBOARD
# ============================================================

@app.route("/user")
@app.route("/user/dashboard")
@login_required("user")
def user_dashboard():
    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE id=?",
        (session["user_id"],),
    ).fetchone()

    bookings = db.execute(
        """
        SELECT b.*, p.name AS provider_name
        FROM bookings b
        LEFT JOIN providers p ON p.id=b.provider_id
        WHERE b.user_id=?
        ORDER BY b.id DESC
        """,
        (session["user_id"],),
    ).fetchall()

    providers = db.execute(
        "SELECT * FROM providers ORDER BY id DESC LIMIT 8"
    ).fetchall()

    return render_template(
        "user_dashboard.html",
        user=user,
        bookings=bookings,
        providers=providers,
        services=SERVICES,
        tutor_types=TUTOR_TYPES,
    )


# ============================================================
# SERVICE DETAILS
# ============================================================

@app.route("/services/<path:service_name>")
def service_details(service_name):
    service_name = service_name.strip()
    subservices = SERVICE_CATALOG.get(service_name, [])

    if not subservices:
        return redirect(url_for("home"))

    return render_template(
        "service_details.html",
        service=service_name,
        subservices=subservices,
    )


# ============================================================
# SEARCH PROVIDERS
# ============================================================

@app.route("/search-providers", methods=["GET", "POST"])
def search_providers():
    service = request.values.get("service", "").strip()
    location = request.values.get("location", "").strip()
    work_type = request.values.get("work_type", "").strip()

    providers = []

    if service:
        db = get_db()

        query = """
            SELECT *
            FROM providers
            WHERE service=?
        """
        params = [service]

        if location:
            query += """
                AND (
                    location LIKE ?
                    OR location IS NULL
                    OR location=''
                )
            """
            params.append("%" + location + "%")

        if work_type:
            query += """
                AND (
                    work_type LIKE ?
                    OR work_type IS NULL
                    OR work_type=''
                )
            """
            params.append("%" + work_type + "%")

        query += " ORDER BY id DESC"

        providers = db.execute(query, params).fetchall()

    return render_template(
        "provider_search.html",
        service=service,
        location=location,
        work_type=work_type,
        providers=providers,
        services=SERVICES,
    )


# ============================================================
# BOOK SERVICE
# ============================================================

@app.route("/book", methods=["POST"])
@login_required("user")
def book():
    db = get_db()

    service = request.form.get(
        "service",
        "Other Services",
    )
    provider_id = request.form.get("provider_id") or None
    work_type = request.form.get(
        "work_type",
        "General Service",
    )
    address = request.form.get("address", "")
    booking_date = request.form.get("booking_date", "")

    if provider_id:
        provider = db.execute(
            "SELECT id FROM providers WHERE id=?",
            (provider_id,),
        ).fetchone()

        if not provider:
            provider_id = None

    db.execute(
        """
        INSERT INTO bookings
        (user_id,provider_id,service,work_type,
         address,booking_date,status,created_at)
        VALUES(?,?,?,?,?,?,?,?)
        """,
        (
            session["user_id"],
            provider_id,
            service,
            work_type,
            address,
            booking_date,
            "Pending",
            datetime.now().isoformat(),
        ),
    )

    db.commit()
    flash("Service booked successfully. Your request is Pending.")

    return redirect(url_for("user_dashboard"))


# ============================================================
# CANCEL BOOKING
# ============================================================

@app.route("/booking/<int:booking_id>/cancel", methods=["POST"])
@login_required("user")
def cancel_booking(booking_id):
    db = get_db()

    db.execute(
        """
        UPDATE bookings
        SET status='Cancelled'
        WHERE id=? AND user_id=?
        """,
        (booking_id, session["user_id"]),
    )

    db.commit()
    flash("Booking cancelled.")

    return redirect(url_for("user_dashboard"))


# ============================================================
# USER PROFILE
# ============================================================

@app.route("/user/profile", methods=["GET", "POST"])
@app.route("/profile", methods=["GET", "POST"])
@login_required("user")
def profile():
    db = get_db()

    if request.method == "POST":
        db.execute(
            """
            UPDATE users
            SET name=?, phone=?, address=?
            WHERE id=?
            """,
            (
                request.form.get("name", ""),
                request.form.get("phone", ""),
                request.form.get("address", ""),
                session["user_id"],
            ),
        )
        db.commit()

        session["name"] = request.form.get("name", "")
        flash("Profile updated successfully.")

    user = db.execute(
        "SELECT * FROM users WHERE id=?",
        (session["user_id"],),
    ).fetchone()

    return render_template(
        "profile.html",
        role="user",
        profile=user,
        user=user,
    )


# ============================================================
# PROVIDER DASHBOARD
# ============================================================

@app.route("/provider")
@app.route("/provider/dashboard")
@login_required("provider")
def provider_dashboard():
    db = get_db()

    provider = db.execute(
        "SELECT * FROM providers WHERE id=?",
        (session["user_id"],),
    ).fetchone()

    jobs = db.execute(
        """
        SELECT b.*, u.name AS customer_name,
               u.phone AS customer_phone
        FROM bookings b
        JOIN users u ON u.id=b.user_id
        WHERE b.provider_id=? OR b.provider_id IS NULL
        ORDER BY b.id DESC
        """,
        (session["user_id"],),
    ).fetchall()

    return render_template(
        "provider_dashboard.html",
        provider=provider,
        jobs=jobs,
    )


# ============================================================
# PROVIDER JOB ACTION
# ============================================================

@app.route(
    "/provider/job/<int:booking_id>/<action>",
    methods=["POST"],
)
@login_required("provider")
def provider_job_action(booking_id, action):
    if action not in ("Accepted", "Rejected", "Completed"):
        flash("Invalid work action.")
        return redirect(url_for("provider_dashboard"))

    db = get_db()

    if action == "Accepted":
        db.execute(
            """
            UPDATE bookings
            SET provider_id=?, status='Accepted'
            WHERE id=? AND
            (provider_id IS NULL OR provider_id=?)
            """,
            (
                session["user_id"],
                booking_id,
                session["user_id"],
            ),
        )
    else:
        db.execute(
            """
            UPDATE bookings
            SET status=?
            WHERE id=? AND provider_id=?
            """,
            (
                action,
                booking_id,
                session["user_id"],
            ),
        )

    db.commit()
    flash(f"Work marked as {action}.")

    return redirect(url_for("provider_dashboard"))


# ============================================================
# PROVIDER PROFILE
# ============================================================

@app.route("/provider/profile", methods=["GET", "POST"])
@login_required("provider")
def provider_profile():
    db = get_db()

    if request.method == "POST":
        service = request.form.get(
            "service",
            "Other Services",
        )

        if service not in SERVICE_NAMES:
            service = "Other Services"

        db.execute(
            """
            UPDATE providers
            SET name=?, phone=?, service=?, work_type=?,
                experience=?, qualification=?, location=?, pricing=?
            WHERE id=?
            """,
            (
                request.form.get("name", ""),
                request.form.get("phone", ""),
                service,
                request.form.get("work_type", ""),
                request.form.get("experience", ""),
                request.form.get("qualification", ""),
                request.form.get("location", ""),
                request.form.get("pricing", ""),
                session["user_id"],
            ),
        )

        db.commit()
        session["name"] = request.form.get("name", "")
        flash("Service provider profile updated.")

    provider = db.execute(
        "SELECT * FROM providers WHERE id=?",
        (session["user_id"],),
    ).fetchone()

    return render_template(
        "provider_profile.html",
        provider=provider,
        services=SERVICE_NAMES,
    )


# ============================================================
# PROVIDER ANALYSIS
# ============================================================

@app.route("/provider/analysis")
@login_required("provider")
def provider_analysis():
    db = get_db()

    total = db.execute(
        "SELECT COUNT(*) AS n FROM bookings WHERE provider_id=?",
        (session["user_id"],),
    ).fetchone()["n"]

    accepted = db.execute(
        """
        SELECT COUNT(*) AS n
        FROM bookings
        WHERE provider_id=? AND status='Accepted'
        """,
        (session["user_id"],),
    ).fetchone()["n"]

    completed = db.execute(
        """
        SELECT COUNT(*) AS n
        FROM bookings
        WHERE provider_id=? AND status='Completed'
        """,
        (session["user_id"],),
    ).fetchone()["n"]

    pending = db.execute(
        """
        SELECT COUNT(*) AS n
        FROM bookings
        WHERE provider_id=? AND status='Pending'
        """,
        (session["user_id"],),
    ).fetchone()["n"]

    rejected = db.execute(
        """
        SELECT COUNT(*) AS n
        FROM bookings
        WHERE provider_id=? AND status='Rejected'
        """,
        (session["user_id"],),
    ).fetchone()["n"]

    return render_template(
        "provider_analysis.html",
        total=total,
        accepted=accepted,
        completed=completed,
        pending=pending,
        rejected=rejected,
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin")
@app.route("/admin/dashboard")
@login_required("admin")
def admin_dashboard():
    db = get_db()

    counts = {
        "users": db.execute(
            "SELECT COUNT(*) AS n FROM users"
        ).fetchone()["n"],

        "providers": db.execute(
            "SELECT COUNT(*) AS n FROM providers"
        ).fetchone()["n"],

        "assigned": db.execute(
            """
            SELECT COUNT(*) AS n FROM bookings
            WHERE provider_id IS NOT NULL
            """
        ).fetchone()["n"],

        "completed": db.execute(
            """
            SELECT COUNT(*) AS n FROM bookings
            WHERE status='Completed'
            """
        ).fetchone()["n"],

        "pending": db.execute(
            """
            SELECT COUNT(*) AS n FROM bookings
            WHERE status='Pending'
            """
        ).fetchone()["n"],

        "accepted": db.execute(
            """
            SELECT COUNT(*) AS n FROM bookings
            WHERE status='Accepted'
            """
        ).fetchone()["n"],

        "rejected": db.execute(
            """
            SELECT COUNT(*) AS n FROM bookings
            WHERE status='Rejected'
            """
        ).fetchone()["n"],

        "cancelled": db.execute(
            """
            SELECT COUNT(*) AS n FROM bookings
            WHERE status='Cancelled'
            """
        ).fetchone()["n"],
    }

    users = db.execute(
        """
        SELECT id,name,email,phone,created_at
        FROM users
        ORDER BY id DESC
        LIMIT 10
        """
    ).fetchall()

    providers = db.execute(
        """
        SELECT id,name,email,service,experience,location
        FROM providers
        ORDER BY id DESC
        LIMIT 10
        """
    ).fetchall()

    bookings = db.execute(
        """
        SELECT b.*, u.name AS customer_name,
               p.name AS provider_name
        FROM bookings b
        JOIN users u ON u.id=b.user_id
        LEFT JOIN providers p ON p.id=b.provider_id
        ORDER BY b.id DESC
        LIMIT 15
        """
    ).fetchall()

    return render_template(
        "admin_dashboard.html",
        counts=counts,
        users=users,
        providers=providers,
        bookings=bookings,
    )


# ============================================================
# ADMIN USERS
# ============================================================

@app.route("/admin/users")
@login_required("admin")
def admin_users():
    db = get_db()

    users = db.execute(
        "SELECT * FROM users ORDER BY id DESC"
    ).fetchall()

    return render_template(
        "admin_users.html",
        users=users,
    )


# ============================================================
# ADMIN PROVIDERS
# ============================================================

@app.route("/admin/providers")
@login_required("admin")
def admin_providers():
    db = get_db()

    providers = db.execute(
        "SELECT * FROM providers ORDER BY id DESC"
    ).fetchall()

    return render_template(
        "admin_providers.html",
        providers=providers,
    )


# ============================================================
# ADMIN BOOKINGS
# ============================================================

@app.route("/admin/bookings")
@login_required("admin")
def admin_bookings():
    db = get_db()

    bookings = db.execute(
        """
        SELECT b.*, u.name AS customer_name,
               p.name AS provider_name
        FROM bookings b
        JOIN users u ON u.id=b.user_id
        LEFT JOIN providers p ON p.id=b.provider_id
        ORDER BY b.id DESC
        """
    ).fetchall()

    return render_template(
        "admin_bookings.html",
        bookings=bookings,
    )


# ============================================================
# ADMIN SERVICES
# ============================================================

@app.route("/admin/services")
@login_required("admin")
def admin_services():
    return render_template(
        "admin_services.html",
        services=SERVICES,
        service_catalog=SERVICE_CATALOG,
        tutor_types=TUTOR_TYPES,
    )


# ============================================================
# ADMIN REVIEWS
# ============================================================

@app.route("/admin/reviews")
@login_required("admin")
def admin_reviews():
    db = get_db()

    reviews = db.execute(
        """
        SELECT r.*, u.name AS user_name,
               p.name AS provider_name
        FROM reviews r
        JOIN users u ON u.id=r.user_id
        LEFT JOIN providers p ON p.id=r.provider_id
        ORDER BY r.id DESC
        """
    ).fetchall()

    return render_template(
        "admin_reviews.html",
        reviews=reviews,
    )


# ============================================================
# USER REVIEW
# ============================================================

@app.route("/review/<int:booking_id>", methods=["POST"])
@login_required("user")
def review(booking_id):
    db = get_db()

    booking = db.execute(
        """
        SELECT * FROM bookings
        WHERE id=? AND user_id=?
        """,
        (
            booking_id,
            session["user_id"],
        ),
    ).fetchone()

    if not booking:
        flash("Booking not found.")
        return redirect(url_for("user_dashboard"))

    try:
        rating = int(request.form.get("rating", "5"))
    except ValueError:
        rating = 5

    rating = max(1, min(5, rating))

    # Prevent duplicate review for the same booking.
    existing = db.execute(
        """
        SELECT 1 FROM reviews
        WHERE booking_id=? AND user_id=?
        """,
        (
            booking_id,
            session["user_id"],
        ),
    ).fetchone()

    if existing:
        flash("You have already reviewed this booking.")
        return redirect(url_for("user_dashboard"))

    db.execute(
        """
        INSERT INTO reviews
        (booking_id,user_id,provider_id,rating,review,created_at)
        VALUES(?,?,?,?,?,?)
        """,
        (
            booking_id,
            session["user_id"],
            booking["provider_id"],
            rating,
            request.form.get("review", ""),
            datetime.now().isoformat(),
        ),
    )

    db.commit()
    flash("Thank you for your rating and review.")

    return redirect(url_for("user_dashboard"))


# ============================================================
# ABOUT
# ============================================================

@app.route("/about")
def about():
    return render_template(
        "simple.html",
        title="About Seva Mithra",
        content=(
            "Seva Mithra connects customers with trusted local "
            "professionals for everyday services and tutoring."
        ),
    )


# ============================================================
# CONTACT
# ============================================================

@app.route("/contact")
def contact():
    return render_template(
        "simple.html",
        title="Contact Us",
        content=(
            "For this project prototype, contact details can be "
            "connected to your college or project team information."
        ),
    )


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        "simple.html",
        title="Page Not Found",
        content="The page you requested could not be found.",
    ), 404


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    init_db()
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG", "1") == "1",
    )