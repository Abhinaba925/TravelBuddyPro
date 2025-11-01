import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
import pydeck as pdk
import re
from dotenv import load_dotenv
from fpdf import FPDF
from urllib.parse import quote
from datetime import datetime, timedelta

# --- Load Environment Variables ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# --- CONFIGURE GEMINI API AT THE START ---
if not API_KEY:
    st.error("🚨 Google API Key not found. Please set it in your .env file.")
else:
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        st.error(f"Failed to configure Gemini API: {e}")

# --- Page Configuration ---
st.set_page_config(
    page_title="TravelBuddy Pro",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading & Icon ---
ICON_URL = "https://img.icons8.com/plasticine/100/000000/marker.png"
ICON_DATA = {
    "url": ICON_URL,
    "width": 128,
    "height": 128,
    "anchorY": 128,
}

def get_city_data():
    """Returns a DataFrame of Indian cities with coordinates."""
    data = {
        'city': ['Mumbai', 'Delhi', 'Bengaluru', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Goa', 'Kochi', 'Varanasi', 'Agra', 'Rishikesh', 'Shimla', 'Darjeeling', 'Udaipur', 'Amritsar'],
        'lat': [19.0760, 28.6139, 12.9716, 13.0827, 22.5726, 17.3850, 18.5204, 23.0225, 26.9124, 15.2993, 9.9312, 25.3176, 27.1767, 30.0869, 31.1048, 27.0360, 24.5854, 31.6340],
        'lon': [72.8777, 77.2090, 77.5946, 80.2707, 88.3639, 78.4867, 73.8567, 72.5714, 75.7873, 74.1240, 76.2673, 82.9739, 78.0081, 78.2676, 77.1734, 88.2627, 73.6826, 74.8723]
    }
    return pd.DataFrame(data)

CITIES_DF = get_city_data()

# --- Helper Functions ---
def extract_locations(text):
    """Extracts place names, days, and coordinates from the itinerary text."""
    pattern = r"\*\*([\w\s,'-]+\w)\*\*\s*\((.*?)\)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    locations_found = []
    if not matches:
        return pd.DataFrame(columns=['name', 'day', 'lat', 'lon'])

    day_rx = re.compile(r'day:\s*(\d+)', re.IGNORECASE)
    lat_rx = re.compile(r'lat:\s*([\d.-]+)', re.IGNORECASE)
    lon_rx = re.compile(r'lon:\s*([\d.-]+)', re.IGNORECASE)

    for name, details in matches:
        day_match = day_rx.search(details)
        lat_match = lat_rx.search(details)
        lon_match = lon_rx.search(details)

        if day_match and lat_match and lon_match:
            locations_found.append({
                'name': name.strip(),
                'day': day_match.group(1),
                'lat': lat_match.group(1),
                'lon': lon_match.group(1)
            })
    
    if not locations_found:
        return pd.DataFrame(columns=['name', 'day', 'lat', 'lon'])
        
    df = pd.DataFrame(locations_found)
    df['day'] = pd.to_numeric(df['day'])
    df['lat'] = pd.to_numeric(df['lat'])
    df['lon'] = pd.to_numeric(df['lon'])
    df['icon_data'] = [ICON_DATA] * len(df)
    return df

def generate_travel_plan(origin, destination, start_date_str, end_date_str, duration, travelers, budget, interests, language):
    """Generates a personalized travel plan using the Gemini API."""
    if not API_KEY:
        return None
    try:
        full_prompt = f"""
        You are an expert travel planner named TravelBuddy. Your response must be in {language}.
        Create a complete travel plan for a trip from {origin} to {destination}, starting on {start_date_str} and ending on {end_date_str}.
        This is a {duration}-day trip for {travelers} people with a {budget} budget, focusing on {', '.join(interests)}.

        Your response MUST use the following specific tags and format:

        [TRIP_SUMMARY]
        A brief, engaging summary.

        [BUDGET_ALLOCATION]
        A Markdown table for the budget.

        [DAY_BY_DAY_ITINERARY]
        A detailed day-by-day plan. For each specific point of interest (like a monument, restaurant, or park), YOU MUST format it as: **Name of Place** (day: X, lat: XX.XXXX, lon: YY.YYYY).
        Example: The plan is to visit **Baga Beach** (day: 1, lat: 15.5560, lon: 73.7517).

        [ACCOMMODATION_SUGGESTIONS]
        List 2-3 accommodation options. For each, use the same format as above, using the arrival day (day: 1).
        Example: Stay at **Taj Fort Aguada Resort & Spa** (day: 1, lat: 15.4957, lon: 73.7667).

        [TRANSPORTATION_TIPS]
        Provide brief advice.
        """
        model = genai.GenerativeModel('gemini-2.5-flash') 
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred: {e}. Please check your API key and network connection.")
        return f"An error occurred: {e}. Please check your API key and network connection."

def generate_packing_list(itinerary_context):
    """Generates a packing list based on the itinerary."""
    if not API_KEY:
        return "API Key is missing."
    try:
        prompt = f"""
        Based on the following travel itinerary:
        ---
        {itinerary_context}
        ---
        Generate a detailed packing list. Group items by category (e.g., Clothing, Toiletries, Electronics, Documents).
        Be smart about the list; for example, if the plan mentions 'trekking', add hiking shoes. If it mentions 'beach', add swimwear.
        """
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating packing list: {e}"

def generate_local_guide(destination, language):
    """Generates a local guide for the destination."""
    if not API_KEY:
        return "API Key is missing."
    try:
        local_language_prompt = f"What is the primary local language spoken in {destination}? Just answer with the name of the language (e.g., 'Hindi', 'Marathi', 'Bengali')."
        model_lang = genai.GenerativeModel('gemini-2.5-flash')
        response_lang = model_lang.generate_content(local_language_prompt)
        local_language = response_lang.text.strip()
        
        prompt = f"""
        You are a friendly local guide for a tourist visiting {destination}.
        Generate a concise 'Know Before You Go' guide. The response must be in {language}.
        Include these sections, formatted with Markdown:
        
        1.  **Must-Try Local Foods:** (List 3-5 specific dishes, not restaurants).
        2.  **Cultural Etiquette:** (e.g., tipping, greetings, dress code for temples).
        3.  **Common Scams to Watch Out For:** (Briefly describe 2-3 common local scams).
        4.  **Basic Phrases in {local_language}:** (Provide 5-7 basic phrases like 'Hello', 'Thank You' in {local_language} with phonetic pronunciation for an {language} speaker).
        """
        model_guide = genai.GenerativeModel('gemini-2.5-flash')
        response_guide = model_guide.generate_content(prompt)
        return response_guide.text
    except Exception as e:
        return f"Error generating local guide: {e}"

def generate_modified_plan(day_content, reason, destination, language):
    """Generates a modified plan for a specific day."""
    if not API_KEY:
        return "API Key is missing."
        
    reason_prompt = ""
    if reason == "rainy":
        reason_prompt = f"It is now raining. Please generate a new, 'rainy day' version of this plan for {destination}. Focus on high-quality indoor activities (like museums, cafes, indoor markets, or cultural centers) that are logically close to the original locations."
    elif reason == "low_energy":
        reason_prompt = f"The user is feeling tired and wants a low-energy, more relaxed version of this plan for {destination}. Please generate a new plan that replaces high-energy activities with restful ones (like a relaxed walk in a park, a scenic cafe, a spa, or a shorter sightseeing trip)."

    try:
        prompt = f"""
        You are a dynamic travel planner. The user's original plan is:
        ---
        {day_content}
        ---
        
        The user's situation has changed: {reason_prompt}
        
        Generate a new, modified plan for this day. Respond in {language}.
        Ensure you keep the same Markdown formatting, including the bolded day title (e.g., **Day X...**) and any location formatting (like **Name of Place** (day: X, ...)).
        """
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error modifying plan: {e}"

def parse_plan(plan_text):
    """Parses the generated plan text using unique identifiers."""
    try:
        sections = {
            "summary": plan_text.split("[TRIP_SUMMARY]")[1].split("[BUDGET_ALLOCATION]")[0],
            "budget": plan_text.split("[BUDGET_ALLOCATION]")[1].split("[DAY_BY_DAY_ITINERARY]")[0],
            "itinerary": plan_text.split("[DAY_BY_DAY_ITINERARY]")[1].split("[ACCOMMODATION_SUGGESTIONS]")[0],
            "accommodation": plan_text.split("[ACCOMMODATION_SUGGESTIONS]")[1].split("[TRANSPORTATION_TIPS]")[0],
            "transport": plan_text.split("[TRANSPORTATION_TIPS]")[1]
        }
        return sections
    except IndexError:
        st.error("⚠️ Failed to parse the AI's response. The structure might be incorrect. Please try generating again.")
        return None

class PDF(FPDF):
    def header(self):
        try:
            self.add_font('NotoSans', '', 'fonts/NotoSansDevanagari-Regular.ttf')
            self.set_font('NotoSans', size=12)
        except RuntimeError:
            self.set_font('Arial', size=12)
            st.warning("NotoSans font not found. PDF output may not support all languages.")
        self.cell(0, 10, 'Your TravelBuddy Itinerary', 0, 1, 'C')
        self.ln(10)
    def footer(self):
        self.set_y(-15)
        try:
            self.set_font('NotoSans', size=8)
        except RuntimeError:
            self.set_font('Arial', size=8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    def chapter_title(self, title):
        try:
            self.set_font('NotoSans', size=14)
        except RuntimeError:
            self.set_font('Arial', 'B', size=14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)
    def chapter_body(self, body):
        try:
            self.set_font('NotoSans', size=11)
        except RuntimeError:
            self.set_font('Arial', size=11)
        self.multi_cell(0, 7, body.encode('latin-1', 'replace').decode('latin-1'))
        self.ln()

def create_pdf(plan_data, destination):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf_plan_data = {
        f"Trip to {destination}": plan_data['summary'],
        "Budget Allocation": plan_data['budget'],
        "Day-by-Day Itinerary": plan_data['itinerary'],
        "Accommodation Suggestions": plan_data['accommodation'],
        "Transportation Tips": plan_data['transport']
    }
    for title, body in pdf_plan_data.items():
        pdf.chapter_title(title.replace("_", " ").title())
        pdf.chapter_body(body.strip())
    
    return bytes(pdf.output(dest='S'))

# --- (FIXED) display_day_plan now extracts its own locations ---
def display_day_plan(day_content, day_num, is_modified=False):
    """Displays the itinerary for a single day."""
    
    day_title = f"Day {day_num}"
    if is_modified:
        day_title += " 🔄 (Modified)"
    
    with st.expander(day_title, expanded=True):
        st.markdown(day_content.strip())
        
        # --- (THE FIX) ---
        # Extract locations from the *current* content, not the old global list
        current_locations = extract_locations(day_content) 
        
        if not current_locations.empty:
            st.markdown("**Locations for this Day:**")
            for index, loc in current_locations.iterrows(): # Loop over the new list
                st.write(f"📍 {loc['name']}")
        # --- (END OF FIX) ---
        
        # --- JOURNAL FEATURE ---
        st.markdown("---")
        st.subheader("My Journal for this Day")
        st.text_area(
            "My Notes:", 
            key=f"journal_notes_day_{day_num}", 
            help="Your notes are saved as you type."
        )
        st.file_uploader(
            "Upload Photos:", 
            key=f"journal_photos_day_{day_num}",
            type=["jpg", "png", "jpeg"],
            accept_multiple_files=True
        )
# --- (END) ---

# --- Initialize Session State ---
if 'plan' not in st.session_state:
    st.session_state.plan = None
if 'selected_day' not in st.session_state:
    st.session_state.selected_day = "All"
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'packing_list' not in st.session_state:
    st.session_state.packing_list = None
if 'itinerary_context' not in st.session_state:
    st.session_state.itinerary_context = None
if 'local_guide' not in st.session_state:
    st.session_state.local_guide = None
if 'modified_plans' not in st.session_state:
    st.session_state.modified_plans = {}
if 'itinerary_days_split' not in st.session_state:
    st.session_state.itinerary_days_split = []

# --- CHATBOT INITIALIZATION ---
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat' not in st.session_state:
    if API_KEY:
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            st.session_state.chat = model.start_chat(history=[])
        except Exception as e:
            st.error(f"Failed to initialize chat model: {e}")
            st.session_state.chat = None
    else:
        st.session_state.chat = None

# --- App Header ---
st.title("TravelBuddy Pro ✈️")
st.markdown("Your interactive AI trip planner for unforgettable Indian holidays.")
st.markdown("---")

# --- Sidebar ---
with st.sidebar:
    st.header("Build Your Trip 📝")

    # CSS to make the emergency button red
    st.markdown("""
    <style>
    a[href="https://www.google.com/maps/search/hospitals+near+me"] {
        background-color: #FF4B4B !important;
        color: white !important;
    }
    a[href="https://www.google.com/maps/search/hospitals+near+me"]:hover {
        background-color: #FF2E2E !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.link_button(
        "➕ Medical Emergency (Hospitals Near Me)", 
        "https://www.google.com/maps/search/hospitals+near+me", 
        use_container_width=True
    )
    st.markdown("---")

    st.subheader("📍 Locations")
    origin = st.selectbox("From:", CITIES_DF['city'].unique(), index=1)
    destination = st.selectbox("To:", CITIES_DF['city'].unique(), index=9)
    
    st.subheader("🗓️ Dates & Guests")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date", 
            value=datetime.now(),
            min_value=datetime.now().date(),
        )
    with col2:
        end_date = st.date_input(
            "End Date", 
            value=start_date + timedelta(days=5),
            min_value=start_date,
        )
    
    travelers = st.number_input("Travelers", min_value=1, max_value=10, value=2)

    st.subheader("⚙️ Personalization")
    budget = st.select_slider("Select Your Budget:", options=["💰 Budget", "💰💰 Mid-Range", "💰💰💰 Luxury"], value="💰💰 Mid-Range")
    interests = st.multiselect("Select Your Interests:", ["🏞️ Adventure", "🏛️ History & Culture", "🍽️ Food", "🧘‍♀️ Wellness", "🎉 Nightlife", "🛍️ Shopping"], default=["🧘‍♀️ Wellness", "🍽️ Food"])
    language = st.selectbox("Select Language:", ["English", "Hindi (हिन्दी)", "Bengali (বাংলা)", "Telugu (తెలుగు)"])
    st.markdown("---")
    
    if st.button("Generate My Travel Plan", use_container_width=True, type="primary"):
        if not API_KEY:
            st.error("Cannot generate plan. Google API Key is missing.")
        else:
            duration = (end_date - start_date).days + 1
            if duration <= 0:
                 st.error("Error: The trip must be at least 1 day long.")
            else:
                st.session_state.selected_day = "All"
                with st.spinner("TravelBuddy is crafting your personalized journey... 🧘"):
                    start_date_str = start_date.strftime("%B %d, %Y")
                    end_date_str = end_date.strftime("%B %d, %Y")
                    plan_output = generate_travel_plan(
                        origin, destination, 
                        start_date_str, end_date_str, duration,
                        travelers, budget, interests, language
                    )
                    
                    if plan_output and "An error occurred" not in plan_output:
                        st.session_state.plan = plan_output
                        
                        st.session_state.packing_list = None
                        st.session_state.local_guide = None
                        st.session_state.modified_plans = {}
                        
                        parsed_plan_for_context = parse_plan(plan_output)
                        st.session_state.itinerary_context = f"SUMMARY: {parsed_plan_for_context['summary']}\nITINERARY: {parsed_plan_for_context['itinerary']}"
                        
                        # --- (FIX) Split and store the itinerary days ---
                        itinerary_days_split = re.split(r'(?=\*\*\s*Day\s*\d+)', parsed_plan_for_context['itinerary'], flags=re.IGNORECASE)
                        st.session_state.itinerary_days_split = [d.strip() for d in itinerary_days_split if d.strip()]
                        # --- (END) ---
                        
                        st.session_state.messages = []
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        st.session_state.chat = model.start_chat(history=[])
                        st.session_state.messages.append({"role": "assistant", "content": "I've loaded your new trip plan! Ask me anything about it."})
                    else:
                        st.session_state.plan = None

    # --- EXPENSE TRACKER UI ---
    st.markdown("---")
    st.header("💸 Expense Tracker")
    
    with st.form(key="expense_form", clear_on_submit=True):
        item = st.text_input("Expense Item (e.g., Cab, Food):")
        amount = st.number_input("Amount (₹):", min_value=0.0, format="%.2f", step=10.0)
        submitted = st.form_submit_button("Add Expense", use_container_width=True)

    if submitted and item and amount > 0:
        st.session_state.expenses.append({'item': item, 'amount': amount})
        st.rerun() 

    if st.session_state.expenses:
        total_expense = sum(e['amount'] for e in st.session_state.expenses)
        st.subheader(f"Total Expense: ₹{total_expense:.2f}")
        
        if st.button("Split Equally", use_container_width=True):
            split_expense = total_expense / travelers
            st.info(f"Split per ({travelers}) Traveler: ₹{split_expense:.2f}")

        st.markdown("**Expense Details:**")
        for i, exp in enumerate(reversed(st.session_state.expenses)):
            st.write(f"- {exp['item']}: ₹{exp['amount']}")

        if st.button("Clear All Expenses", use_container_width=True):
            st.session_state.expenses = []
            st.rerun()
    else:
        st.write("No expenses added yet.")
    
    # --- CONTEXT-AWARE CHATBOT ---
    st.markdown("---")
    st.header("🤖 Ask Anything")
    
    if not API_KEY or st.session_state.chat is None:
        st.warning("Please add your Google API Key in the `.env` file to use the chatbot.")
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask about your plan..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            final_prompt = prompt
            if st.session_state.itinerary_context:
                final_prompt = f"""
                HERE IS THE USER'S ITINERARY FOR CONTEXT:
                ---
                {st.session_state.itinerary_context}
                ---
                NOW, PLEASE ANSWER THE USER'S QUESTION: "{prompt}"
                """
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = st.session_state.chat.send_message(final_prompt)
                        response_text = response.text
                    except Exception as e:
                        response_text = f"An error occurred: {e}"
                    st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

# --- Main Content Area ---
if st.session_state.plan:
    dest_coords = CITIES_DF[CITIES_DF['city'] == destination].iloc[0]
    parsed_plan = parse_plan(st.session_state.plan)

    if parsed_plan:
        st.header(f"Your Custom Itinerary: {origin} to {destination}")
        st.write(parsed_plan['summary'])
        
        st.subheader("Book Your Trip & Services")
        flight_url = "https://www.easemytrip.com/flights"
        hotel_url = "https://www.easemytrip.com/hotels"
        uber_url = "https://www.uber.com"
        restaurants_url = "http://googleusercontent.com/maps/google.com/1"
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("✈️ Search Flights", flight_url, use_container_width=True)
            st.link_button("🚕 Ride with Uber", uber_url, use_container_width=True)
        with col2:
            st.link_button("🏨 Book Hotels", hotel_url, use_container_width=True)
            st.link_button("🍽️ Find Restaurants Nearby", restaurants_url, use_container_width=True)

        st.markdown("---")
        st.subheader("🧳 Your Trip Toolkit")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate AI Packing List 🧳", use_container_width=True):
                with st.spinner("Analyzing your itinerary to create a packing list..."):
                    itinerary_context = f"SUMMARY: {parsed_plan['summary']}\nITINERARY: {parsed_plan['itinerary']}"
                    packing_list = generate_packing_list(itinerary_context)
                    st.session_state.packing_list = packing_list
        with col2:
            if st.button("Generate AI Local Guide 📜", use_container_width=True):
                with st.spinner(f"Generating local guide for {destination}..."):
                    local_guide = generate_local_guide(destination, language)
                    st.session_state.local_guide = local_guide

        if st.session_state.packing_list:
            with st.expander("Your Custom Packing List", expanded=False):
                st.markdown(st.session_state.packing_list)
        
        if st.session_state.local_guide:
            with st.expander("Your AI Local Guide", expanded=False):
                st.markdown(st.session_state.local_guide)
                
        st.markdown("---")
        
        all_locations = extract_locations(parsed_plan['itinerary'] + parsed_plan['accommodation'])
        day_numbers = sorted(all_locations['day'].unique())

        st.subheader("📍 Interactive Trip Map")
        st.pydeck_chart(pdk.Deck(
            map_style='https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
            initial_view_state=pdk.ViewState(latitude=dest_coords['lat'], longitude=dest_coords['lon'], zoom=11, pitch=50),
            layers=[
                pdk.Layer('IconLayer', data=all_locations, get_icon='icon_data', get_position='[lon, lat]',
                          get_size=4, size_scale=15, pickable=True)
            ],
            tooltip={"html": "<b>{name}</b>", "style": {"color": "black", "background-color": "white"}}
        ))

        st.markdown("---")
        st.subheader("Change of Plans?")
        if day_numbers:
            selected_day_num = st.selectbox("Which day do you want to change?", day_numbers, format_func=lambda x: f"Day {x}")
            
            original_day_content = ""
            # --- (FIXED) Loop through the *stored split itinerary* ---
            for content in st.session_state.itinerary_days_split:
                if re.search(rf'\*\*Day {selected_day_num}\b', content, re.IGNORECASE):
                    original_day_content = content
                    break
            
            replanner_cols = st.columns(2)
            if replanner_cols[0].button("Rainy Day ☔", use_container_width=True):
                with st.spinner(f"Finding rainy day activities for Day {selected_day_num}..."):
                    modified_plan = generate_modified_plan(original_day_content, "rainy", destination, language)
                    st.session_state.modified_plans[selected_day_num] = modified_plan
                    st.rerun()

            if replanner_cols[1].button("Low Energy 😴", use_container_width=True):
                with st.spinner(f"Finding relaxed activities for Day {selected_day_num}..."):
                    modified_plan = generate_modified_plan(original_day_content, "low_energy", destination, language)
                    st.session_state.modified_plans[selected_day_num] = modified_plan
                    st.rerun()
        
        st.markdown("---")
        st.markdown("#### Day-by-Day Plan & Journal")
        
        if day_numbers:
            # --- (FIXED) Use tabs for clean day-by-day display ---
            day_tabs = st.tabs([f"Day {d}" for d in day_numbers])
            
            for i, day_num in enumerate(day_numbers):
                with day_tabs[i]:
                    original_content_for_day = ""
                    # --- (FIXED) Loop through the *stored split itinerary* ---
                    for content in st.session_state.itinerary_days_split:
                         if re.search(rf'\*\*Day {day_num}\b', content, re.IGNORECASE):
                            original_content_for_day = content
                            break

                    is_modified = day_num in st.session_state.modified_plans
                    day_content_to_display = st.session_state.modified_plans.get(day_num, original_content_for_day)
                    
                    if day_content_to_display:
                        # --- (FIXED) Call the updated function with the correct args ---
                        display_day_plan(day_content_to_display, day_num, is_modified=is_modified)
                    else:
                        st.warning(f"Could not find itinerary content for Day {day_num}.")
            # --- (END OF FIX) ---
        else:
            st.warning("No day-by-day itinerary was found in the plan.")

        st.markdown("---")
        
        with st.expander("🏨 Accommodation Suggestions", expanded=True):
            accommodation_locations = extract_locations(parsed_plan['accommodation'])
            
            if accommodation_locations.empty:
                st.markdown(parsed_plan['accommodation'])
            else:
                st.markdown("Here are some AI-powered suggestions. Click to search on EaseMyTrip.")
                for index, loc in accommodation_locations.iterrows():
                    search_term = f"{loc['name']}, {destination}"
                    emt_url = f"https://www.easemytrip.com/hotels/search-hotels/?search={quote(search_term)}"
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"🏨 **{loc['name']}**")
                    with col2:
                        st.link_button("Book on EaseMyTrip", emt_url, use_container_width=True)

        with st.expander("💰 Budget Breakdown"):
            st.markdown(parsed_plan['budget'])
        
        pdf_bytes = create_pdf(parsed_plan, destination)
        st.download_button(label="📥 Download Itinerary as PDF", data=pdf_bytes, file_name=f"TravelBuddy_Itinerary_{destination}.pdf", mime="application/octet-stream")

# Disclaimer
st.markdown("---")
st.warning("Disclaimer: TravelBuddy is a prototype. All recommendations should be independently verified.", icon="⚠️")
