import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime

# Configure Gemini API (Use a valid API Key)
API_KEY = "AIzaSyDVCS2lIuFteH_cS-5NqlW3yQoiOPPlxFM"  # Replace with your actual key
genai.configure(api_key=API_KEY)

def get_travel_options(source, destination, date):
    """
    Fetches travel options using Gemini AI and returns a structured JSON response.
    """
    model = genai.GenerativeModel("gemini-1.5-pro")  
    prompt = f"""
    You are a travel assistant. Provide structured travel options from {source} to {destination} on {date}.
    Return ONLY JSON, without explanations, like this:

    {{
        "flights": [{{"airline": "IndiGo", "departure": "06:00", "arrival": "08:05", "duration": "2h 05m", "cost": 12000}}],
        "trains": [{{"name": "Rajdhani Express", "departure": "18:00", "arrival": "08:00", "duration": "14h", "cost": 2500}}],
        "buses": [{{"operator": "VRL Travels", "departure": "21:00", "arrival": "07:00", "duration": "10h", "cost": 1500}}],
        "cabs": [{{"cost": 8000, "duration": "9h"}}]
    }}
    """

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip() if hasattr(response, 'text') else ""

        # Debugging: Print raw response in Streamlit
        st.write("AI Raw Response:", response_text)

        # Extract only valid JSON part
        json_start = response_text.find("{")
        json_end = response_text.rfind("}")
        if json_start != -1 and json_end != -1:
            json_data = response_text[json_start:json_end+1]  # Extract JSON portion
            travel_data = json.loads(json_data)
            return travel_data
        else:
            return {"error": "Invalid JSON format received from AI. Check response structure."}

    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON. Check AI response."}
    except Exception as e:
        return {"error": str(e)}

def generate_summary(travel_data):
    """
    Generates a summary of the best travel options.
    """
    summary = "### 🔹 Travel Recommendations Summary:\n"
    all_options = []
    
    if "flights" in travel_data:
        all_options.extend([("Flight", flight["cost"]) for flight in travel_data["flights"]])
    if "trains" in travel_data:
        all_options.extend([("Train", train["cost"]) for train in travel_data["trains"]])
    if "buses" in travel_data:
        all_options.extend([("Bus", bus["cost"]) for bus in travel_data["buses"]])
    if "cabs" in travel_data:
        all_options.extend([("Cab", cab["cost"]) for cab in travel_data["cabs"]])
    
    if all_options:
        best_option = min(all_options, key=lambda x: x[1])
        summary += f"✔ The cheapest option is *{best_option[0]}* at ₹{best_option[1]}.\n"
    
    if "flights" in travel_data:
        summary += "⚡ The fastest option is *Flight* (around 1-2 hours).\n"
    
    return summary

# Streamlit UI
st.title("🌍 AI-Powered Travel Planner")
st.write("Find the best travel options between your source and destination.")

source = st.text_input("Enter Source Location")
destination = st.text_input("Enter Destination")
date = st.date_input("Select Travel Date", min_value=datetime.today())

if st.button("Explore Travel Plans", use_container_width=True):
    if source and destination:
        result = get_travel_options(source, destination, date.strftime("%Y-%m-%d"))

        if "error" in result:
            st.error(result["error"])
        else:
            st.write(f"Okay, I have found the best travel options from *{source}* to *{destination}* on *{date.strftime('%B %d, %Y')}*.")
            st.write("---")
            
            summary = generate_summary(result)
            st.markdown(summary)

            if result.get("flights"):
                st.subheader("✈ Flights")
                for flight in result["flights"]:
                    st.markdown(f"""
                    - *{flight['airline']}*
                      - 🕒 Departure: {flight['departure']}
                      - 🛬 Arrival: {flight['arrival']}
                      - ⏳ Duration: {flight['duration']}
                      - 💰 Price: ₹{flight['cost']}
                    """)

            if result.get("trains"):
                st.subheader("🚆 Trains")
                for train in result["trains"]:
                    st.markdown(f"""
                    - *{train['name']}*
                      - 🕒 Departure: {train['departure']}
                      - 🛬 Arrival: {train['arrival']}
                      - ⏳ Duration: {train['duration']}
                      - 💰 Price: ₹{train['cost']}
                    """)

            if result.get("buses"):
                st.subheader("🚌 Buses")
                for bus in result["buses"]:
                    st.markdown(f"""
                    - *{bus['operator']}*
                      - 🕒 Departure: {bus['departure']}
                      - 🛬 Arrival: {bus['arrival']}
                      - ⏳ Duration: {bus['duration']}
                      - 💰 Price: ₹{bus['cost']}
                    """)

            if result.get("cabs"):
                st.subheader("🚖 Cabs")
                for cab in result["cabs"]:
                    st.markdown(f"""
                    - *Private Cab*
                      - ⏳ Duration: {cab['duration']}
                      - 💰 Price: ₹{cab['cost']}
                    """)
    else:
        st.error("Please enter both source and destination.")
