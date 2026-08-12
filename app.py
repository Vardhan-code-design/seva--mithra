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


# ============================================================
# DUMMY PROVIDERS
# ============================================================

DUMMY_PROVIDERS = {

    "Electrician": [
        (
            "Arjun Electricals",
            "9876501001",
            "Repair & Installation",
            "8 years",
            "ITI Electrical",
            "Hyderabad",
            "₹299 onwards"
        ),
        (
            "PowerFix Solutions",
            "9876501002",
            "Home Wiring & Repairs",
            "5 years",
            "Diploma Electrical",
            "Hyderabad",
            "₹349 onwards"
        ),
        (
            "BrightWire Services",
            "9876501003",
            "Installation & Inspection",
            "11 years",
            "ITI + Safety Certified",
            "Hyderabad",
            "₹499 onwards"
        ),
    ],

    "Plumber": [
        (
            "Sai Plumbing Works",
            "9876501101",
            "Bathroom & Kitchen Plumbing",
            "7 years",
            "ITI Plumbing",
            "Hyderabad",
            "₹249 onwards"
        ),
        (
            "AquaFix Experts",
            "9876501102",
            "Leakage & Pipe Repair",
            "4 years",
            "Plumbing Certificate",
            "Hyderabad",
            "₹299 onwards"
        ),
        (
            "FlowPro Services",
            "9876501103",
            "Water Tank & Motor Service",
            "10 years",
            "ITI Plumbing",
            "Hyderabad",
            "₹399 onwards"
        ),
    ],

    "Cleaning": [
        (
            "CleanNest Services",
            "9876501201",
            "Home & Deep Cleaning",
            "6 years",
            "Professional Cleaning Certified",
            "Hyderabad",
            "₹499 onwards"
        ),
        (
            "SparkleCare",
            "9876501202",
            "Kitchen & Bathroom Cleaning",
            "3 years",
            "Cleaning Specialist",
            "Hyderabad",
            "₹399 onwards"
        ),
        (
            "FreshHome Experts",
            "9876501203",
            "Full Home & Office Cleaning",
            "9 years",
            "Facility Management",
            "Hyderabad",
            "₹699 onwards"
        ),
    ],

    "AC Repair": [
        (
            "CoolCare AC",
            "9876501301",
            "AC Repair & Gas Filling",
            "9 years",
            "ITI Refrigeration",
            "Hyderabad",
            "₹399 onwards"
        ),
        (
            "ChillTech Services",
            "9876501302",
            "Installation & Maintenance",
            "5 years",
            "Diploma HVAC",
            "Hyderabad",
            "₹449 onwards"
        ),
        (
            "AirPro Experts",
            "9876501303",
            "PCB & Compressor Repair",
            "12 years",
            "HVAC Certified",
            "Hyderabad",
            "₹599 onwards"
        ),
    ],

    "Carpenter": [
        (
            "WoodCraft Works",
            "9876501401",
            "Furniture Repair",
            "8 years",
            "ITI Carpenter",
            "Hyderabad",
            "₹349 onwards"
        ),
        (
            "HomeWood Experts",
            "9876501402",
            "Doors & Wardrobes",
            "5 years",
            "Carpentry Certified",
            "Hyderabad",
            "₹399 onwards"
        ),
        (
            "FineWood Studio",
            "9876501403",
            "Custom Woodwork",
            "13 years",
            "Master Carpenter",
            "Hyderabad",
            "₹699 onwards"
        ),
    ],

    "Painting": [
        (
            "ColorNest Painters",
            "9876501501",
            "Interior Painting",
            "6 years",
            "Painting Specialist",
            "Hyderabad",
            "₹1,499/room"
        ),
        (
            "PerfectCoat Services",
            "9876501502",
            "Exterior & Waterproof Painting",
            "9 years",
            "Certified Painter",
            "Hyderabad",
            "₹2,499/room"
        ),
        (
            "BrushPro Experts",
            "9876501503",
            "Texture & Premium Painting",
            "12 years",
            "Advanced Painting Certified",
            "Hyderabad",
            "₹3,499/room"
        ),
    ],

    "Appliance Repair": [
        (
            "QuickFix Appliances",
            "9876501601",
            "Refrigerator & Washing Machine",
            "7 years",
            "ITI Electronics",
            "Hyderabad",
            "₹299 onwards"
        ),
        (
            "HomeTech Repairs",
            "9876501602",
            "TV & Microwave Repair",
            "4 years",
            "Diploma Electronics",
            "Hyderabad",
            "₹249 onwards"
        ),
        (
            "ApplianceCare Pro",
            "9876501603",
            "Geyser & Water Purifier",
            "10 years",
            "Electronics Certified",
            "Hyderabad",
            "₹399 onwards"
        ),
    ],

    "Tutor": [
        (
            "Anjali Sharma",
            "9876501701",
            "Mathematics & Science",
            "6 years",
            "M.Sc + B.Ed",
            "Hyderabad",
            "₹450/hour"
        ),
        (
            "Rahul Verma",
            "9876501702",
            "Computer / Programming",
            "4 years",
            "M.Tech CSE",
            "Hyderabad",
            "₹600/hour"
        ),
        (
            "Priya Reddy",
            "9876501703",
            "English & School Tuition",
            "9 years",
            "M.A + B.Ed",
            "Hyderabad",
            "₹400/hour"
        ),
    ],

    "Beauty Services": [
        (
            "GlowAtHome",
            "9876501801",
            "Facial & Skin Care",
            "6 years",
            "Beauty Academy Certified",
            "Hyderabad",
            "₹599 onwards"
        ),
        (
            "StylePro Beauty",
            "9876501802",
            "Hair Styling & Makeup",
            "4 years",
            "Professional Makeup Artist",
            "Hyderabad",
            "₹799 onwards"
        ),
        (
            "BlushBeauty Experts",
            "9876501803",
            "Bridal & Event Makeup",
            "10 years",
            "Advanced Beauty Certified",
            "Hyderabad",
            "₹1,499 onwards"
        ),
    ],

    "Other Services": [
        (
            "HomeAssist Services",
            "9876501901",
            "General Handyman",
            "7 years",
            "Multi-skill Certified",
            "Hyderabad",
            "₹299 onwards"
        ),
        (
            "FixMate Solutions",
            "9876501902",
            "CCTV & Wi-Fi Setup",
            "5 years",
            "Diploma Electronics",
            "Hyderabad",
            "₹399 onwards"
        ),
        (
            "CarePlus Services",
            "9876501903",
            "Gardening & Pest Control",
            "8 years",
            "Service Professional Certified",
            "Hyderabad",
            "₹499 onwards"
        ),
    ],
}


# ============================================================
# SERVICE CATALOG
# ============================================================

SERVICE_CATALOG = {

    "Electrician": [
        "Fan Installation",
        "Switch & Socket Repair",
        "Light Installation",
        "Wiring & Rewiring",
        "MCB / Fuse Repair",
        "Inverter Installation",
        "Doorbell Installation",
        "Power Point Installation",
        "Electrical Inspection",
        "Short Circuit Repair"
    ],

    "Plumber": [
        "Tap Repair",
        "Pipe Leakage Repair",
        "Wash Basin Installation",
        "Toilet Repair",
        "Water Tank Service",
        "Drain Cleaning",
        "Shower Installation",
        "Kitchen Sink Repair",
        "Bathroom Plumbing",
        "Water Motor Repair"
    ],

    "Cleaning": [
        "Full Home Cleaning",
        "Deep Cleaning",
        "Kitchen Cleaning",
        "Bathroom Cleaning",
        "Sofa Cleaning",
        "Carpet Cleaning",
        "Window Cleaning",
        "Move-in Cleaning",
        "Move-out Cleaning",
        "Office Cleaning"
    ],

    "AC Repair": [
        "AC General Service",
        "AC Gas Filling",
        "AC Installation",
        "AC Uninstallation",
        "AC Cooling Repair",
        "Water Leakage Repair",
        "AC PCB Repair",
        "AC Compressor Check",
        "AC Filter Cleaning",
        "AC Annual Service"
    ],

    "Carpenter": [
        "Furniture Repair",
        "Door Repair",
        "Door Installation",
        "Wardrobe Repair",
        "Table Repair",
        "Chair Repair",
        "Shelf Installation",
        "Curtain Rod Installation",
        "Bed Repair",
        "Custom Woodwork"
    ],

    "Painting": [
        "Room Painting",
        "Full Home Painting",
        "Exterior Painting",
        "Wall Texture",
        "Ceiling Painting",
        "Door Painting",
        "Metal Painting",
        "Waterproof Painting",
        "Office Painting",
        "Color Consultation"
    ],

    "Appliance Repair": [
        "Refrigerator Repair",
        "Washing Machine Repair",
        "Microwave Repair",
        "TV Repair",
        "Water Purifier Repair",
        "Geyser Repair",
        "Chimney Repair",
        "Mixer Grinder Repair",
        "Dishwasher Repair",
        "Air Cooler Repair"
    ],

    "Tutor": [
        "School Tuition",
        "Mathematics",
        "Science",
        "Computer / Programming",
        "English",
        "Other Languages",
        "College Subjects",
        "Competitive Exam Preparation",
        "Home Tutor",
        "Online Tutor"
    ],

    "Beauty Services": [
        "Haircut at Home",
        "Hair Styling",
        "Facial",
        "Manicure",
        "Pedicure",
        "Threading",
        "Waxing",
        "Makeup",
        "Hair Spa",
        "Bridal / Event Makeup"
    ],

    "Other Services": [
        "Pest Control",
        "Gardening",
        "Packers & Movers Help",
        "Laundry Service",
        "Car Wash",
        "CCTV Installation",
        "Wi-Fi / Router Setup",
        "Computer Repair",
        "Mobile Repair",
        "General Handyman"
    ]
}


TUTOR_TYPES = [
    "School Tuition",
    "Mathematics",
    "Science",
    "Computer / Programming",
    "English",
    "Other Languages",
    "College Subjects",
    "Competitive Exam Preparation",
    "Home Tutor",
    "Online Tutor"
]


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

    if db:
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

    # ========================================================
    # DEMO USER
    # ========================================================

    if not cur.execute(
        "SELECT 1 FROM users WHERE email=?",
        ("user@demo.com",)
    ).fetchone():

        cur.execute(
            """
            INSERT INTO users
            (name