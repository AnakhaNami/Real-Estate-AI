import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# ── Connect to Firebase ───────────────────────────────────────────────────────
# This runs once. It reads your firebase_key.json and connects to Firestore.
KEY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    os.getenv("FIREBASE_KEY_PATH", "firebase_key.json")
)

if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ── Collection names ──────────────────────────────────────────────────────────
# Think of these as folder names in Firebase.
# builders/ contains all builder documents
# agents/   contains all agent documents
# projects/ contains all project documents
# users/    contains user profiles
# chat_history/ contains every message sent

COL_BUILDERS = "builders"
COL_AGENTS   = "agents"
COL_PROJECTS = "projects"
COL_USERS    = "users"
COL_HISTORY  = "chat_history"

# ══════════════════════════════════════════════════════════════════════════════
# SEED DATA
# This is the Kerala real estate data we store in Firebase.
# Run this once and it uploads everything to the cloud.
# ══════════════════════════════════════════════════════════════════════════════

BUILDERS_DATA = [
    dict(
        name="Sobha Limited", city="Thrissur", established=1995,
        rera_id="K-RERA-B-001", total_projects=42, completed=38,
        ongoing=4, rating=4.5,
        speciality="Luxury apartments and villas",
        contact_email="info@sobha.com", website="www.sobha.com",
        description=(
            "Sobha Limited is one of India's most reputed real estate developers "
            "with a strong presence across Kerala. Known for superior construction "
            "quality, premium finishes, and consistent on-time delivery. "
            "Active in Thrissur, Kochi, and Kozhikode with both apartment and "
            "villa projects. Sobha self-develops all its projects meaning they "
            "do not outsource construction — this ensures quality control."
        )
    ),
    dict(
        name="Confident Group", city="Kochi", established=2000,
        rera_id="K-RERA-B-002", total_projects=35, completed=30,
        ongoing=5, rating=4.2,
        speciality="Mid-segment smart apartments",
        contact_email="info@confidentgroup.in", website="www.confidentgroup.in",
        description=(
            "Confident Group is a Kerala-based developer with strong projects "
            "in Kochi and Thiruvananthapuram. Popular for tech-enabled smart home "
            "apartments at mid-segment pricing. Offers flexible payment plans "
            "and all projects are RERA-compliant. Known for good after-sales service "
            "and active resident communities in completed projects."
        )
    ),
    dict(
        name="Skyline Builders", city="Kozhikode", established=1998,
        rera_id="K-RERA-B-003", total_projects=28, completed=25,
        ongoing=3, rating=4.0,
        speciality="Affordable to mid-range flats in Malabar region",
        contact_email="info@skylinebuilders.in", website="www.skylinebuilders.in",
        description=(
            "Skyline Builders is a Kozhikode-based developer with 25 years of "
            "experience in the Malabar real estate market. Specialises in "
            "well-located apartments in Calicut city and its suburbs. "
            "Known for transparent pricing, clean legal titles, and strong "
            "customer support. Popular among Gulf NRI buyers from the Malabar region."
        )
    ),
    dict(
        name="Puravankara", city="Kochi", established=1975,
        rera_id="K-RERA-B-004", total_projects=80, completed=70,
        ongoing=10, rating=4.3,
        speciality="Premium and luxury residential complexes",
        contact_email="enquiry@puravankara.com", website="www.puravankara.com",
        description=(
            "Puravankara is a pan-India premium developer with significant projects "
            "in Kochi. Operates two brands — Puravankara for luxury and Provident "
            "for affordable housing. Strong resale value track record across all "
            "cities. Listed company on BSE and NSE, adding credibility and financial "
            "transparency for buyers."
        )
    ),
    dict(
        name="Asset Homes", city="Thiruvananthapuram", established=2003,
        rera_id="K-RERA-B-005", total_projects=20, completed=17,
        ongoing=3, rating=3.9,
        speciality="Budget to mid-segment flats in Trivandrum",
        contact_email="info@assethomes.in", website="www.assethomes.in",
        description=(
            "Asset Homes is a Thiruvananthapuram-focused developer targeting "
            "government employees, teachers, and IT sector workers. Offers "
            "competitive pricing with essential amenities. Good connectivity "
            "to Technopark and Secretariat in most projects. Offers flexible "
            "payment plans aligned with home loan disbursement schedules."
        )
    ),
    dict(
        name="UBL Group", city="Kochi", established=2005,
        rera_id="K-RERA-B-006", total_projects=15, completed=12,
        ongoing=3, rating=4.1,
        speciality="Waterfront and ultra-premium apartments in Kochi",
        contact_email="info@ublgroup.in", website="www.ublgroup.in",
        description=(
            "UBL Group is a boutique Kochi developer known for premium waterfront "
            "apartments in prime locations like Marine Drive and Edapally. "
            "Smaller portfolio but very high build quality and unique locations. "
            "Projects have strong rental yield potential due to prime addresses."
        )
    ),
]

AGENTS_DATA = [
    dict(
        name="Rajan Pillai", city="Kochi",
        locality="Kakkanad, Edapally, Aluva, Ernakulam city",
        rera_id="K-RERA-A-101", experience_yrs=12,
        languages="Malayalam, English, Hindi",
        speciality="IT corridor apartments and investment properties",
        rating=4.7, deals_closed=340, phone="+91-98470-11001",
        description=(
            "Rajan Pillai is a senior real estate agent with 12 years of experience "
            "in the Kochi IT corridor. Expert in Kakkanad, Edapally, and Aluva "
            "localities. Specialises in helping IT professionals and NRI buyers "
            "find good investment properties. Known for honest advice and "
            "transparent brokerage. Helps NRI clients with remote purchase process "
            "including power of attorney arrangements."
        )
    ),
    dict(
        name="Sreeja Nair", city="Kozhikode",
        locality="Calicut city, Chevayur, Feroke, Beypore",
        rera_id="K-RERA-A-102", experience_yrs=8,
        languages="Malayalam, English",
        speciality="First-time buyers and budget apartments",
        rating=4.5, deals_closed=210, phone="+91-94470-22002",
        description=(
            "Sreeja Nair is a Kozhikode-based agent with a strong reputation for "
            "ethical practice and patience with first-time buyers. She specialises "
            "in guiding new buyers through the entire process from search to "
            "registration. Strong knowledge of Kozhikode's local property market "
            "and RERA compliance. Highly recommended for buyers who feel overwhelmed "
            "by the property buying process."
        )
    ),
    dict(
        name="Thomas Mathew", city="Thrissur",
        locality="Thrissur city, Ollur, Guruvayur, Irinjalakuda",
        rera_id="K-RERA-A-103", experience_yrs=15,
        languages="Malayalam, English, Tamil",
        speciality="Luxury villas and NRI investment in Thrissur",
        rating=4.8, deals_closed=520, phone="+91-98950-33003",
        description=(
            "Thomas Mathew is the most experienced agent in Thrissur with 15 years "
            "in the luxury segment. Handles high-value villa transactions and NRI "
            "clients extensively. Deep connections with top builders and legal "
            "experts in Thrissur. Known for complete transaction management — "
            "from property search to registration. Tamil-speaking which helps with "
            "buyers from Tamil Nadu investing in Thrissur."
        )
    ),
    dict(
        name="Anitha Krishnan", city="Thiruvananthapuram",
        locality="Pattom, Kowdiar, Vellayambalam, Technopark area",
        rera_id="K-RERA-A-104", experience_yrs=6,
        languages="Malayalam, English",
        speciality="Government sector buyers and Technopark professionals",
        rating=4.3, deals_closed=150, phone="+91-94470-44004",
        description=(
            "Anitha Krishnan focuses on Thiruvananthapuram buyers from the "
            "government and IT sectors. Expert in properties near Secretariat, "
            "KSRTC hub, and Technopark. Good knowledge of Kerala government "
            "employee housing schemes and HUDCO loans. Straightforward and "
            "reliable — popular with first-time buyers in Trivandrum."
        )
    ),
    dict(
        name="Mohammed Ashraf", city="Kozhikode",
        locality="Palayam, Mavoor Road, Nadakkavu, Calicut Beach area",
        rera_id="K-RERA-A-105", experience_yrs=10,
        languages="Malayalam, English, Arabic",
        speciality="Gulf NRI buyers and Calicut city centre properties",
        rating=4.6, deals_closed=290, phone="+91-98460-55005",
        description=(
            "Mohammed Ashraf is the top NRI specialist in Kozhikode, primarily "
            "serving Gulf-based Malayalis looking to invest in Kerala property. "
            "Arabic-speaking — very popular among the Gulf NRI community in the "
            "Malabar region. Handles power of attorney transactions, remote property "
            "purchases, and complete documentation for NRI buyers. "
            "Strong network with builders offering NRI-specific payment plans."
        )
    ),
]

PROJECTS_DATA = [
    dict(
        name="Sobha City Thrissur", builder_name="Sobha Limited",
        city="Thrissur", locality="Punkunnam",
        project_type="Apartment",
        bhk_options="2BHK, 3BHK, 4BHK",
        price_min_lakhs=85.0, price_max_lakhs=180.0,
        area_sqft_min=1100, area_sqft_max=2400,
        total_units=320, available_units=45,
        possession_year=2025,
        rera_number="K-RERA-PRJ-2021-001",
        amenities="Swimming pool, fully equipped gym, clubhouse, children's play area, 24hr security, power backup, covered parking, landscaped gardens",
        status="Ready to move",
        description=(
            "Sobha City is a premium residential township in the heart of Thrissur. "
            "Offers 2BHK, 3BHK, and 4BHK apartments with Sobha's signature quality "
            "finishes. Walking distance to Thrissur city centre, Round, and major "
            "hospitals. Strong investment option — Sobha brand ensures good resale value."
        )
    ),
    dict(
        name="Confident Adora", builder_name="Confident Group",
        city="Kochi", locality="Kakkanad",
        project_type="Apartment",
        bhk_options="2BHK, 3BHK",
        price_min_lakhs=65.0, price_max_lakhs=95.0,
        area_sqft_min=950, area_sqft_max=1450,
        total_units=200, available_units=32,
        possession_year=2025,
        rera_number="K-RERA-PRJ-2022-002",
        amenities="Gym, rooftop garden, EV charging stations, smart home automation, CCTV, power backup, visitor parking",
        status="Ready to move",
        description=(
            "Confident Adora is a smart apartment project in Kakkanad IT corridor, "
            "ideal for IT professionals at Infopark and SmartCity. Offers smart home "
            "features like app-controlled lights and security at mid-segment pricing. "
            "Excellent connectivity to NH bypass and metro."
        )
    ),
    dict(
        name="Skyline Azur", builder_name="Skyline Builders",
        city="Kozhikode", locality="Chevayur",
        project_type="Apartment",
        bhk_options="2BHK, 3BHK",
        price_min_lakhs=48.0, price_max_lakhs=72.0,
        area_sqft_min=880, area_sqft_max=1350,
        total_units=120, available_units=28,
        possession_year=2026,
        rera_number="K-RERA-PRJ-2023-003",
        amenities="Gym, children's play area, covered parking, power backup, intercom, CCTV",
        status="Under construction",
        description=(
            "Skyline Azur offers affordable quality apartments in Chevayur, one of "
            "Kozhikode's most desirable residential localities. Close to beaches, "
            "good schools, and medical facilities. Good road connectivity to "
            "Calicut city centre and Calicut International Airport."
        )
    ),
    dict(
        name="Puravankara Zenium", builder_name="Puravankara",
        city="Kochi", locality="Edapally",
        project_type="Apartment",
        bhk_options="3BHK, 4BHK",
        price_min_lakhs=120.0, price_max_lakhs=210.0,
        area_sqft_min=1600, area_sqft_max=2800,
        total_units=180, available_units=20,
        possession_year=2025,
        rera_number="K-RERA-PRJ-2021-004",
        amenities="Olympic-size pool, fully equipped gym, sky lounge, concierge service, EV charging, landscaped gardens, multiplex cinema room",
        status="Ready to move",
        description=(
            "Puravankara Zenium is an ultra-premium residential project at Edapally "
            "junction — one of Kochi's most strategic locations on the NH bypass. "
            "Strong investment value with high rental demand from corporates. "
            "Limited inventory with only 20 units remaining."
        )
    ),
    dict(
        name="Asset Jasmine", builder_name="Asset Homes",
        city="Thiruvananthapuram", locality="Pattom",
        project_type="Apartment",
        bhk_options="2BHK, 3BHK",
        price_min_lakhs=55.0, price_max_lakhs=80.0,
        area_sqft_min=950, area_sqft_max=1400,
        total_units=90, available_units=15,
        possession_year=2024,
        rera_number="K-RERA-PRJ-2022-005",
        amenities="Gym, children's park, covered parking, solar panels, rainwater harvesting, CCTV",
        status="Ready to move",
        description=(
            "Asset Jasmine offers well-priced apartments in Pattom, one of "
            "Thiruvananthapuram's most premium localities. Close to Secretariat, "
            "top schools, and Technopark. Popular with government officers and "
            "IT professionals. Solar panels reduce electricity costs for residents."
        )
    ),
    dict(
        name="Skyline Ocean Pearl", builder_name="Skyline Builders",
        city="Kozhikode", locality="Beypore",
        project_type="Apartment",
        bhk_options="2BHK, 3BHK",
        price_min_lakhs=52.0, price_max_lakhs=78.0,
        area_sqft_min=920, area_sqft_max=1380,
        total_units=96, available_units=41,
        possession_year=2026,
        rera_number="K-RERA-PRJ-2023-006",
        amenities="Sea view balconies, gym, party hall, children's pool, covered parking, landscaped courtyard",
        status="Under construction",
        description=(
            "Skyline Ocean Pearl is a sea-facing apartment project in Beypore with "
            "partial sea views from upper floors. Popular with Gulf NRI buyers from "
            "the Malabar region. Close to Beypore port and upcoming Kozhikode "
            "metro corridor. Strong rental potential from NRI and tourist demand."
        )
    ),
    dict(
        name="Confident Nesto Smart City", builder_name="Confident Group",
        city="Kochi", locality="Aluva",
        project_type="Integrated Township",
        bhk_options="1BHK, 2BHK, 3BHK",
        price_min_lakhs=38.0, price_max_lakhs=75.0,
        area_sqft_min=620, area_sqft_max=1350,
        total_units=450, available_units=120,
        possession_year=2027,
        rera_number="K-RERA-PRJ-2024-007",
        amenities="Commercial zone, gym, swimming pool, school on campus, supermarket, food court, EV charging, jogging track",
        status="Under construction",
        description=(
            "Confident Nesto Smart City is an integrated township in Aluva combining "
            "residential and commercial zones. Best value-for-money project in greater "
            "Kochi area with 1BHK starting at just Rs.38 lakhs. Excellent connectivity "
            "via NH bypass and upcoming metro extension to Aluva."
        )
    ),
    dict(
        name="UBL Marina Heights", builder_name="UBL Group",
        city="Kochi", locality="Marine Drive",
        project_type="Ultra-luxury Apartment",
        bhk_options="3BHK, 4BHK, Penthouse",
        price_min_lakhs=185.0, price_max_lakhs=420.0,
        area_sqft_min=1800, area_sqft_max=4200,
        total_units=60, available_units=8,
        possession_year=2025,
        rera_number="K-RERA-PRJ-2022-008",
        amenities="Infinity pool, private jetty access, sky bar, concierge, valet parking, gym, spa, private theatre",
        status="Ready to move",
        description=(
            "UBL Marina Heights offers ultra-luxury waterfront apartments on Marine "
            "Drive — the most prestigious address in Kochi. Backwater and sea views "
            "from all floors. Only 60 units total with 8 remaining. Strong investment "
            "and high rental yield potential due to unique waterfront location."
        )
    ),
]

# ══════════════════════════════════════════════════════════════════════════════
# SEED FUNCTION — uploads all data to Firebase
# ══════════════════════════════════════════════════════════════════════════════

def seed_firestore():
    """
    Uploads all builders, agents, and projects to Firebase Firestore.
    Clears existing data first so you can re-run safely.
    """
    print("\nConnecting to Firebase Firestore...")

    for col_name, data_list, label in [
        (COL_BUILDERS, BUILDERS_DATA, "builders"),
        (COL_AGENTS,   AGENTS_DATA,   "agents"),
        (COL_PROJECTS, PROJECTS_DATA, "projects"),
    ]:
        # Delete old documents
        old_docs = db.collection(col_name).stream()
        for doc in old_docs:
            doc.reference.delete()

        # Upload new documents
        for item in data_list:
            item_copy = item.copy()
            item_copy["created_at"] = datetime.utcnow()
            # Create readable ID from name
            doc_id = item["name"].lower().replace(" ", "_").replace(".", "")
            db.collection(col_name).document(doc_id).set(item_copy)

        print(f"  Uploaded {len(data_list)} {label} to Firebase")

    print("\nAll data is now live in Firebase Firestore!")
    print("Open https://console.firebase.google.com to see it.\n")

# ══════════════════════════════════════════════════════════════════════════════
# SEARCH FUNCTIONS — query Firebase and return matching records
# ══════════════════════════════════════════════════════════════════════════════

def search_projects(city=None, max_budget=None, bhk=None, status=None, locality=None):
    """
    Searches the projects collection in Firebase.
    Filters by city, budget, BHK type, and status.
    Returns a list of matching project dictionaries.
    """
    query = db.collection(COL_PROJECTS)

    # Firebase can filter by exact city match directly
    if city:
        query = query.where("city", "==", city)
    if status:
        query = query.where("status", "==", status)

    # Fetch results and apply remaining filters in Python
    results = [doc.to_dict() for doc in query.stream()]

    if max_budget:
        results = [p for p in results
                   if p.get("price_min_lakhs", 9999) <= float(max_budget)]
    if bhk:
        results = [p for p in results
                   if bhk in p.get("bhk_options", "")]
    if locality:
        results = [p for p in results
                   if locality.lower() in p.get("locality", "").lower()]

    results.sort(key=lambda x: x.get("price_min_lakhs", 0))
    return results


def search_builders(city=None, name=None):
    """
    Searches the builders collection in Firebase.
    Filters by city or partial name match.
    Returns builders sorted by rating (highest first).
    """
    query = db.collection(COL_BUILDERS)
    if city:
        query = query.where("city", "==", city)

    results = [doc.to_dict() for doc in query.stream()]

    if name:
        results = [b for b in results
                   if name.lower() in b.get("name", "").lower()]

    results.sort(key=lambda x: x.get("rating", 0), reverse=True)
    return results


def search_agents(city=None, speciality=None, language=None):
    """
    Searches the agents collection in Firebase.
    Filters by city, speciality, or language.
    Returns agents sorted by rating (highest first).
    """
    query = db.collection(COL_AGENTS)
    if city:
        query = query.where("city", "==", city)

    results = [doc.to_dict() for doc in query.stream()]

    if speciality:
        results = [a for a in results
                   if speciality.lower() in a.get("speciality", "").lower()]
    if language:
        results = [a for a in results
                   if language.lower() in a.get("languages", "").lower()]

    results.sort(key=lambda x: x.get("rating", 0), reverse=True)
    return results

# ══════════════════════════════════════════════════════════════════════════════
# TEXT CONVERSION — turns database results into readable sentences for the AI
# ══════════════════════════════════════════════════════════════════════════════

def projects_to_text(projects: list) -> str:
    """Converts a list of project dicts into a readable paragraph for the AI."""
    if not projects:
        return "No matching projects found in the Kerala database."
    lines = []
    for p in projects:
        lines.append(
            f"Project '{p['name']}' by {p['builder_name']} is located in "
            f"{p['locality']}, {p['city']}. It offers {p['bhk_options']} apartments "
            f"priced between Rs.{p['price_min_lakhs']} and Rs.{p['price_max_lakhs']} lakhs, "
            f"with sizes from {p['area_sqft_min']} to {p['area_sqft_max']} sqft. "
            f"Current status is {p['status']} with possession expected in {p['possession_year']}. "
            f"There are {p['available_units']} units available out of {p['total_units']} total. "
            f"RERA registration number is {p['rera_number']}. "
            f"Amenities include: {p['amenities']}. "
            f"{p['description']}"
        )
    return "\n\n".join(lines)


def builders_to_text(builders: list) -> str:
    """Converts a list of builder dicts into readable sentences for the AI."""
    if not builders:
        return "No matching builders found in the Kerala database."
    lines = []
    for b in builders:
        lines.append(
            f"{b['name']} is a real estate developer established in {b['established']}, "
            f"headquartered in {b['city']}, Kerala. Their RERA registration ID is {b['rera_id']}. "
            f"They have a rating of {b['rating']} out of 5 and have completed "
            f"{b['completed']} out of {b['total_projects']} projects, with {b['ongoing']} currently ongoing. "
            f"They specialise in {b['speciality']}. "
            f"You can reach them at {b['contact_email']} or visit {b['website']}. "
            f"{b['description']}"
        )
    return "\n\n".join(lines)


def agents_to_text(agents: list) -> str:
    """Converts a list of agent dicts into readable sentences for the AI."""
    if not agents:
        return "No matching agents found in the Kerala database."
    lines = []
    for a in agents:
        lines.append(
            f"{a['name']} is a real estate agent based in {a['city']}, Kerala, "
            f"covering the areas of {a['locality']}. "
            f"They have {a['experience_yrs']} years of experience and a rating of {a['rating']} out of 5, "
            f"with {a['deals_closed']} successful deals closed. "
            f"They speak {a['languages']} and specialise in {a['speciality']}. "
            f"RERA agent ID: {a['rera_id']}. Contact: {a['phone']}. "
            f"{a['description']}"
        )
    return "\n\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# USER PROFILE AND CHAT HISTORY
# ══════════════════════════════════════════════════════════════════════════════

def save_user(name, city, budget_lakhs, bedrooms, loan_eligible=None):
    """Saves a user profile to Firebase and returns their unique ID."""
    _, doc_ref = db.collection(COL_USERS).add({
        "name": name,
        "city": city,
        "budget_lakhs": budget_lakhs,
        "bedrooms": bedrooms,
        "loan_eligible": loan_eligible,
        "created_at": datetime.utcnow()
    })
    return doc_ref.id  # Firebase auto-generates a unique string ID


def get_user(user_id):
    """Retrieves a user profile from Firebase by their ID."""
    doc = db.collection(COL_USERS).document(str(user_id)).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = user_id
        # Convert dict to simple object so user.name, user.city etc. work
        return type("User", (), data)()
    return None


def save_message(user_id, role, message):
    """Saves a single chat message to Firebase."""
    db.collection(COL_HISTORY).add({
        "user_id": str(user_id),
        "role": role,
        "message": message,
        "created_at": datetime.utcnow()
    })


def get_history(user_id, last_n=6):
    """Retrieves the last N messages for a user from Firebase."""
    try:
        docs = (
            db.collection(COL_HISTORY)
            .where("user_id", "==", str(user_id))
            .order_by("created_at")
            .limit_to_last(last_n)
            .stream()
        )
        history = []
        for doc in docs:
            d = doc.to_dict()
            history.append(
                type("Msg", (), {"role": d["role"], "message": d["message"]})()
            )
        return history
    except Exception:
        return []  # Return empty if index not yet built


def init_db():
    pass  # Firebase needs no schema setup — collections create themselves


if __name__ == "__main__":
    seed_firestore()