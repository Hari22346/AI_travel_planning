import os
import re
from datetime import date, datetime

import streamlit as st
from langchain_core.messages import HumanMessage

from main import app


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="HARI — AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

for key, value in {
    "destination": "",
    "origin": "",
    "quick_query": "",
}.items():
    st.session_state.setdefault(key, value)


# ============================================================
# CONSTANTS
# ============================================================

HERO_IMAGE = (
    "https://images.unsplash.com/photo-1436491865332-7a61a109cc05"
    "?auto=format&fit=crop&w=1800&q=90"
)

DESTINATIONS = [
    (
        "🇯🇵 Tokyo",
        "Tokyo",
        "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf"
        "?auto=format&fit=crop&w=700&q=85",
    ),
    (
        "🇫🇷 Paris",
        "Paris",
        "https://images.unsplash.com/photo-1502602898657-3e91760cbb34"
        "?auto=format&fit=crop&w=700&q=85",
    ),
    (
        "🇹🇭 Bangkok",
        "Bangkok",
        "https://images.unsplash.com/photo-1508009603885-50cf7c579365"
        "?auto=format&fit=crop&w=700&q=85",
    ),
    (
        "🇮🇹 Rome",
        "Rome",
        "https://images.unsplash.com/photo-1552832230-c0197dd311b5"
        "?auto=format&fit=crop&w=700&q=85",
    ),
    (
        "🇦🇪 Dubai",
        "Dubai",
        "https://images.unsplash.com/photo-1512453979798-5ea266f8880c"
        "?auto=format&fit=crop&w=700&q=85",
    ),
]

QUICK_TRIPS = [
    "7-day Japan under ₹2L",
    "Paris trip for 5 days",
    "Dubai weekend trip",
    "Bali backpacking 10 days",
]

AGENT_META = {
    "flight_agent": ("✈️", "Flight Agent"),
    "hotel_agent": ("🏨", "Hotel Agent"),
    "itinerary_agent": ("🗺️", "Itinerary Agent"),
    "final_agent": ("🧠", "Final Agent"),
}

TECHNOLOGIES = [
    "🔗 LangGraph",
    "🧠 Groq · LLaMA 3.3 70B",
    "🐘 PostgreSQL",
    "🔍 Tavily Search",
    "✈️ AviationStack",
]

AGENTS = [
    "① Flight Agent",
    "② Hotel Agent",
    "③ Itinerary Agent",
    "④ Final Agent",
]


# ============================================================
# HELPERS
# ============================================================

def html(content):
    st.markdown(content, unsafe_allow_html=True)


def section(title, subtitle=None):
    html(f'<div class="section-title">{title}</div>')

    if subtitle:
        html(f'<div class="section-subtitle">{subtitle}</div>')


def sidebar_list(title, items):
    html(f'<div class="sidebar-section">{title}</div>')

    for item in items:
        html(f'<div class="sidebar-item">{item}</div>')


def duration_days(departure, return_date):
    if departure and return_date:
        return (return_date - departure).days + 1

    return None


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap');

html, body, .stApp {
    font-family: 'DM Sans', sans-serif;
    background:
        radial-gradient(circle at 10% 10%, rgba(255,171,89,.16), transparent 25%),
        radial-gradient(circle at 90% 15%, rgba(255,118,42,.10), transparent 25%),
        linear-gradient(180deg, #fffaf5 0%, #fff7ef 45%, #fffaf7 100%);
    color: #2b211c;
}

.stApp {
    color: #2b211c;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.2rem;
    padding-bottom: 5rem;
}

#MainMenu,
footer,
header {
    visibility: hidden;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #fff7ef 0%,
        #fffdfb 55%,
        #fff4e8 100%
    ) !important;
    border-right: 1px solid #f1dccb;
    box-shadow: 8px 0 30px rgba(119,62,25,.05);
}

section[data-testid="stSidebar"] * {
    color: #4a3327;
}

.sidebar-subtitle {
    color: #9c7964;
    font-size: .75rem;
    margin: .2rem 0 1.5rem;
}

.sidebar-section {
    color: #e86d22;
    font-size: .67rem;
    font-weight: 800;
    letter-spacing: .14em;
    text-transform: uppercase;
    margin: 1.6rem 0 .65rem;
}

.sidebar-item {
    background: rgba(255,255,255,.85);
    border: 1px solid #f1dfd1;
    border-radius: 12px;
    padding: .65rem .75rem;
    margin-bottom: .45rem;
    color: #705646 !important;
    font-size: .8rem;
    transition: all .2s ease;
    box-shadow: 0 4px 15px rgba(130,69,30,.035);
}

.sidebar-item:hover {
    border-color: #f3a36d;
    transform: translateX(3px);
    box-shadow: 0 7px 20px rgba(232,109,34,.10);
}

/* HERO */

.hero-badge {
    text-align: center;
    color: #e76f20;
    font-size: .72rem;
    font-weight: 800;
    letter-spacing: .16em;
    text-transform: uppercase;
    margin-top: .8rem;
}

.hero-title {
    text-align: center;
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.8rem, 5vw, 5.2rem);
    line-height: 1.02;
    font-weight: 800;
    letter-spacing: -.045em;
    color: #2c211b;
    margin: .55rem 0 .7rem;
    text-shadow: 0 5px 25px rgba(151,76,24,.08);
}

.hero-title span {
    background: linear-gradient(100deg,#f06419,#ff9b45,#e95716);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-subtitle {
    max-width: 760px;
    margin: auto;
    text-align: center;
    color: #80695b;
    font-size: .98rem;
    line-height: 1.75;
}

/* SECTIONS */

.section-title {
    color: #30231c;
    font-family: 'Playfair Display', serif;
    font-size: 1.35rem;
    font-weight: 800;
    margin-top: 2.6rem;
    margin-bottom: .2rem;
}

.section-subtitle {
    color: #967b69;
    font-size: .82rem;
    margin-bottom: 1.15rem;
}

/* DESTINATIONS */

.destination-name {
    text-align: center;
    color: #493327;
    font-size: .82rem;
    font-weight: 800;
    margin: .55rem 0;
}

div[data-testid="stImage"] {
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 12px 30px rgba(90,42,17,.10);
}

/* INPUT CONTAINER */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,.88) !important;
    border: 1px solid #efddcf !important;
    border-radius: 22px !important;
    box-shadow: 0 15px 45px rgba(99,50,21,.07) !important;
}

/* INPUTS */

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stDateInput input {
    background: #fffaf7 !important;
    color: #392920 !important;
    border: 1px solid #ead6c7 !important;
    border-radius: 12px !important;
    min-height: 42px;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus,
.stDateInput input:focus {
    border-color: #ed7a31 !important;
    box-shadow: 0 0 0 3px rgba(237,122,49,.12) !important;
    background: white !important;
}

.stTextInput label,
.stNumberInput label,
.stDateInput label,
.stSelectbox label,
.stTextArea label {
    color: #765b4b !important;
    font-size: .75rem !important;
    font-weight: 800 !important;
}

div[data-baseweb="select"] > div {
    background: #fffaf7 !important;
    border-color: #ead6c7 !important;
    color: #392920 !important;
    border-radius: 12px !important;
}

/* BUTTONS */

div.stButton > button {
    background: linear-gradient(
        135deg,
        #f77b2d 0%,
        #e95c18 55%,
        #d94d10 100%
    ) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    min-height: 44px;
    box-shadow: 0 8px 20px rgba(225,91,20,.18);
    transition: all .2s ease !important;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    filter: brightness(1.05);
    box-shadow: 0 13px 28px rgba(225,91,20,.25) !important;
}

div.stButton > button:active {
    transform: translateY(0);
}

div.stButton > button[kind="primary"] {
    min-height: 54px !important;
    font-size: .95rem !important;
    letter-spacing: .02em;
    border-radius: 15px !important;
    box-shadow: 0 12px 30px rgba(224,83,14,.22);
}

/* STATUS */

[data-testid="stStatusWidget"] {
    background: rgba(255,255,255,.92) !important;
    border: 1px solid #efdccc !important;
    border-radius: 15px !important;
    box-shadow: 0 8px 25px rgba(95,47,21,.06);
}

[data-testid="stStatusWidget"] * {
    color: #513b2d !important;
}

/* MARKDOWN */

.stMarkdown h1,
.stMarkdown h2,
.stMarkdown h3 {
    color: #35271f !important;
    font-family: 'Playfair Display', serif;
}

.stMarkdown p,
.stMarkdown li {
    color: #654f41;
    line-height: 1.7;
}

.stMarkdown strong {
    color: #3c2a20;
}

/* FLIGHTS */

.flight-card {
    background: linear-gradient(135deg,#ffffff,#fff7f0);
    border: 1px solid #efd9c8;
    border-radius: 18px;
    padding: 1.15rem 1.3rem;
    margin: .7rem 0;
    box-shadow: 0 12px 30px rgba(102,48,18,.07);
    position: relative;
    overflow: hidden;
}

.flight-card::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: linear-gradient(180deg,#ff9c52,#e85a18);
}

.flight-name {
    color: #392920;
    font-size: 1rem;
    font-weight: 800;
}

.flight-route {
    color: #806859;
    font-size: .82rem;
    margin: .35rem 0;
}

.flight-time {
    color: #4c3629;
    font-size: .92rem;
    font-weight: 700;
}

.flight-price {
    color: #e6601c;
    font-size: 1rem;
    font-weight: 800;
    margin-top: .3rem;
}

/* METRICS */

.metric-card {
    background: linear-gradient(145deg,#ffffff,#fff7f0);
    border: 1px solid #efd9c8;
    border-radius: 18px;
    padding: 1.1rem;
    text-align: center;
    box-shadow: 0 10px 28px rgba(102,50,20,.06);
}

.metric-number {
    color: #e7621c;
    font-size: 1.65rem;
    font-weight: 800;
}

.metric-label {
    color: #9b806e;
    font-size: .68rem;
    text-transform: uppercase;
    letter-spacing: .1em;
}

/* DOWNLOAD */

div[data-testid="stDownloadButton"] button {
    background: #fff3e8 !important;
    color: #d95a18 !important;
    border: 1px solid #efc8aa !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
}

/* FOOTER */

.footer {
    text-align: center;
    color: #a58a78;
    font-size: .72rem;
    margin-top: 5rem;
    padding-top: 1.8rem;
    border-top: 1px solid #efdfd3;
}

@media (max-width: 900px) {
    .hero-title {
        font-size: 3rem;
    }

    .hero-subtitle {
        padding: 0 1rem;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    html(
        """
        <div style="
            display:flex;
            align-items:center;
            gap:.55rem;
            font-family:'Playfair Display',serif;
            font-size:1.45rem;
            font-weight:800;
            color:#2e211a;
            margin-bottom:.15rem;
        ">
            <span style="
                background:linear-gradient(135deg,#ff9a4d,#e95b18);
                -webkit-background-clip:text;
                -webkit-text-fill-color:transparent;
            ">✈</span>
            VoyageAI
        </div>

        <div class="sidebar-subtitle">
            AI-powered travel planning
        </div>
        """
    )

    sidebar_list("SESSION", [])

    thread_id = st.text_input(
        "User ID",
        value="hari_user",
        label_visibility="collapsed",
    )

    sidebar_list("POWERED BY", TECHNOLOGIES)
    sidebar_list("AGENT PIPELINE", AGENTS)

    html('<div class="sidebar-section">ACCURACY</div>')

    st.caption(
        "The planner uses structured trip requirements to reduce "
        "incorrect assumptions about dates, budget, travelers and destinations."
    )


# ============================================================
# HERO
# ============================================================

html(
    f"""
    <div style="
        height:100px;
        overflow:hidden;
        border-radius:16px;
    ">
        <img src="{HERO_IMAGE}"
             style="width:100%;height:100%;object-fit:cover;">
    </div>

    <div class="hero-badge">
        ✦ MULTI-AGENT TRAVEL INTELLIGENCE
    </div>

    <div class="hero-title">
        Plan less.<br>
        <span>Travel better.</span>
    </div>

    <div class="hero-subtitle">
        VoyageAI coordinates specialized AI agents to search flights,
        discover hotels, optimize your itinerary and build a
        personalized trip around your budget.
    </div>
    """
)


# ============================================================
# TRUST FEATURES
# ============================================================

features = [
    ("✈️", "Flight research"),
    ("🏨", "Hotel discovery"),
    ("🗺️", "Smart itinerary"),
    ("💰", "Budget aware"),
]

for col, (icon, label) in zip(st.columns(4), features):
    with col:
        html(
            f"""
            <div style="
                text-align:center;
                padding:.7rem;
                color:#9bb2c8;
                font-size:.78rem;
            ">
                <span style="font-size:1rem">{icon}</span>
                &nbsp; {label}
            </div>
            """
        )


# ============================================================
# DESTINATIONS
# ============================================================

section(
    "🌎 Explore popular destinations",
    "Choose a destination to start building your trip.",
)

for col, (name, destination, image_url) in zip(
    st.columns(len(DESTINATIONS)),
    DESTINATIONS,
):
    with col:
        st.image(image_url, use_container_width=True)
        html(f'<div class="destination-name">{name}</div>')

        if st.button(
            f"Plan {destination}",
            key=f"plan_{destination}",
            use_container_width=True,
        ):
            st.session_state.destination = destination
            st.rerun()


# ============================================================
# TRIP BUILDER
# ============================================================

section(
    "🧭 Build your trip",
    "Provide structured information for a more accurate AI plan.",
)

with st.container(border=True):

    col1, col2 = st.columns(2)

    with col1:
        origin = st.text_input(
            "📍 Departure city",
            value=st.session_state.origin,
            placeholder="e.g. Bengaluru",
        )

    with col2:
        destination = st.text_input(
            "🌎 Destination",
            value=st.session_state.destination,
            placeholder="e.g. Japan",
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        departure_date = st.date_input(
            "🛫 Departure date",
            value=None,
            min_value=date.today(),
        )

    with col2:
        return_date = st.date_input(
            "🛬 Return date",
            value=None,
            min_value=date.today(),
        )

    with col3:
        travelers = st.number_input(
            "👥 Travelers",
            min_value=1,
            max_value=20,
            value=2,
            step=1,
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        budget = st.number_input(
            "💰 Maximum budget",
            min_value=0,
            value=200000,
            step=5000,
        )

    with col2:
        currency = st.selectbox(
            "💱 Currency",
            ["INR", "USD", "EUR", "GBP", "AED", "SGD"],
        )

    with col3:
        travel_style = st.selectbox(
            "✨ Travel style",
            [
                "Balanced",
                "Budget",
                "Luxury",
                "Adventure",
                "Family",
                "Romantic",
                "Business",
            ],
        )

    html(
        """
        <div style="
            color:#7791aa;
            font-size:.7rem;
            font-weight:700;
            text-transform:uppercase;
            letter-spacing:.1em;
            margin-top:.8rem;
            margin-bottom:.5rem;
        ">
            Popular trip ideas
        </div>
        """
    )

    for col, query in zip(st.columns(4), QUICK_TRIPS):
        with col:
            if st.button(
                query,
                key=f"quick_{query}",
                use_container_width=True,
            ):
                st.session_state.quick_query = query
                st.rerun()

    special_requirements = st.text_area(
        "📝 Additional requirements",
        value=st.session_state.quick_query,
        placeholder=(
            "Example: Plan a 7-day Japan trip from Bengaluru for 2 people "
            "under ₹2 lakhs. Include Tokyo and Kyoto, prefer 3–4 star "
            "hotels, avoid overnight flights and include sightseeing."
        ),
        height=120,
    )


# ============================================================
# FLIGHT RENDERER
# ============================================================

def render_flight_cards(text):

    if not text or not text.strip():
        st.caption("No flight data returned.")
        return

    shown = False

    for block in re.split(r"\n\s*\*\s*", text.strip()):

        data = {}

        for line in block.splitlines():
            line = re.sub(r"[*_`#-]+", "", line).strip()
            key, separator, value = line.partition(":")

            if separator:
                data[key.strip().lower()] = value.strip()

        flight = (
            data.get("flight")
            or data.get("airline")
            or data.get("flight name")
        )

        route = data.get("route")
        time = data.get("time") or data.get("schedule")
        price = data.get("price") or data.get("fare")

        if not all((flight, route, time, price)):
            continue

        shown = True

        html(
            f"""
            <div class="flight-card">
                <div class="flight-name">✈️ {flight}</div>
                <div class="flight-route">{route}</div>
                <div class="flight-time">{time}</div>
                <div class="flight-price">{price}</div>
            </div>
            """
        )

    if not shown:
        st.markdown(text)


# ============================================================
# STRUCTURED QUERY
# ============================================================

def build_query(
    origin,
    destination,
    departure_date,
    return_date,
    travelers,
    budget,
    currency,
    travel_style,
    requirements,
):
    duration = duration_days(departure_date, return_date)

    return f"""
TRAVEL REQUEST

Departure city:
{origin}

Destination:
{destination}

Departure date:
{departure_date or "Not specified"}

Return date:
{return_date or "Not specified"}

Trip duration:
{duration or "Not specified"} days

Travelers:
{travelers}

Maximum budget:
{budget} {currency}

Travel style:
{travel_style}

User requirements:
{requirements}

ACCURACY REQUIREMENTS

1. Use the exact departure city.
2. Use the exact destination.
3. Respect the dates provided by the user.
4. Respect the number of travelers.
5. Respect the maximum budget.
6. Use the requested currency.
7. Do not invent flight numbers.
8. Do not invent hotel availability.
9. Do not invent prices.
10. Do not invent schedules.
11. Clearly identify estimated prices.
12. Prefer realistic flight connections.
13. Avoid impossible travel schedules.
14. Keep the itinerary geographically sensible.
15. Cross-check the final itinerary against the flight and hotel results.
16. If reliable live information is unavailable, explicitly state that.
17. Never silently change the user's requirements.

FLIGHT DISPLAY FORMAT

For every flight option you find, return these four fields exactly,
one per line:

FLIGHT: <airline name and flight number>
ROUTE: <departure city> → <arrival city>
TIME: <departure time> → <arrival time>
PRICE: <price with currency>

Do not omit these fields when flight data is available.
"""


# ============================================================
# GENERATE
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

generate = st.button(
    "✨  BUILD MY COMPLETE TRAVEL PLAN",
    use_container_width=True,
    type="primary",
)


# ============================================================
# RUN PIPELINE
# ============================================================

if generate:

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    errors = []

    if not origin.strip():
        errors.append("Please enter your departure city.")

    if not destination.strip():
        errors.append("Please enter your destination.")

    if departure_date and return_date and return_date < departure_date:
        errors.append("Return date cannot be before departure date.")

    if not special_requirements.strip():
        errors.append("Please describe your trip requirements.")

    if errors:
        for error in errors:
            st.error(error)
        st.stop()

    # --------------------------------------------------------
    # REQUEST
    # --------------------------------------------------------

    duration = duration_days(departure_date, return_date)

    structured_query = build_query(
        origin,
        destination,
        departure_date,
        return_date,
        travelers,
        budget,
        currency,
        travel_style,
        special_requirements,
    )

    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

    collected = {
        "flight_results": "",
        "hotel_results": "",
        "itinerary": "",
        "final_response": "",
        "llm_calls": 0,
    }

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    # --------------------------------------------------------
    # PIPELINE
    # --------------------------------------------------------

    section(
        "🤖 AI agents are working",
        "Searching, comparing and optimizing your trip.",
    )

    try:

        for chunk in app.stream(
            {
                "messages": [HumanMessage(content=structured_query)],
                "user_query": structured_query,
                "flight_results": "",
                "hotel_results": "",
                "itinerary": "",
                "llm_calls": 0,
            },
            config=config,
            stream_mode="updates",
        ):

            for node_name, state_update in chunk.items():

                icon, label = AGENT_META.get(
                    node_name,
                    ("🔧", node_name),
                )

                with st.status(
                    f"{icon} {label}",
                    state="complete",
                    expanded=False,
                ):

                    if node_name == "flight_agent":

                        text = state_update.get("flight_results", "")
                        collected["flight_results"] = text

                        render_flight_cards(text)

                    elif node_name == "hotel_agent":

                        text = state_update.get("hotel_results", "")
                        collected["hotel_results"] = text

                        st.markdown(
                            text or "No hotel data returned."
                        )

                    elif node_name == "itinerary_agent":

                        text = state_update.get("itinerary", "")
                        collected["itinerary"] = text

                        st.markdown(
                            text or "No itinerary generated."
                        )

                    elif node_name == "final_agent":

                        messages = state_update.get("messages", [])

                        text = (
                            messages[-1].content
                            if messages
                            else ""
                        )

                        collected["final_response"] = text

                        st.markdown(
                            text or "No final response generated."
                        )

                    collected["llm_calls"] = state_update.get(
                        "llm_calls",
                        collected["llm_calls"],
                    )

    except Exception as error:

        st.error("The AI travel pipeline failed.")
        st.exception(error)
        st.stop()

    # ========================================================
    # METRICS
    # ========================================================

    section("📊 Planning summary")

    metrics = [
        ("4", "Agents"),
        (str(collected["llm_calls"]), "LLM Calls"),
        ("✓", "Completed"),
        (str(duration) if duration else "—", "Trip Days"),
    ]

    for col, (number, label) in zip(st.columns(4), metrics):

        with col:
            html(
                f"""
                <div class="metric-card">
                    <div class="metric-number">{number}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """
            )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    if collected["final_response"]:

        section(
            "🧠 Your personalized travel plan",
            "Built from your destination, dates, budget, traveler count "
            "and preferences.",
        )

        st.markdown(collected["final_response"])

    # ========================================================
    # SAVE PLAN
    # ========================================================

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"travel_plan_{timestamp}.md"

    save_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "travel_plans",
    )

    os.makedirs(save_dir, exist_ok=True)

    file_content = f"""# VoyageAI Travel Plan

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**User ID:** {thread_id}

## Trip Requirements

- Departure: {origin}
- Destination: {destination}
- Departure date: {departure_date}
- Return date: {return_date}
- Duration: {duration or "Not specified"} days
- Travelers: {travelers}
- Budget: {budget} {currency}
- Travel style: {travel_style}

## Additional Requirements

{special_requirements}

---

## ✈️ Flight Information

{collected["flight_results"] or "N/A"}

---

## 🏨 Hotel Information

{collected["hotel_results"] or "N/A"}

---

## 🗺️ Itinerary

{collected["itinerary"] or "N/A"}

---

## 🧠 Final Travel Plan

{collected["final_response"] or "N/A"}

---

**LLM Calls:** {collected["llm_calls"]}
"""

    file_path = os.path.join(save_dir, filename)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(file_content)

    download_col, save_col = st.columns([1, 3])

    with download_col:
        st.download_button(
            "⬇️ Download Plan",
            data=file_content,
            file_name=filename,
            mime="text/markdown",
            use_container_width=True,
        )

    with save_col:
        st.success(
            f"Plan saved to travel_plans/{filename}"
        )


# ============================================================
# FOOTER
# ============================================================

html(
    """
    <div class="footer">
        ✈️ HariAI · Multi-Agent Travel Intelligence<br>
        Flight research · Hotel discovery · Itinerary optimization
    </div>
    """
)