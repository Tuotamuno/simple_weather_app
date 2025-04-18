import streamlit as st
import requests
import geocoder
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim

# Detect user's city via IP
location = geocoder.ip('me')
city_default = location.city if location.ok else "London"

st.set_page_config(page_title="Weather App", layout="centered")

# Define default background color and image
bg_color = "#F0F8FF"
bg_image = "https://images.unsplash.com/photo-1503120912634-0ef76e37fd4f?auto=format&fit=crop&w=1350&q=80"  # A calming landscape view
text_color = "#ffffff"  # white text to fit backgrounds

# Add dark overlay to enhance text visibility
st.markdown(f"""
    <style>
        .stApp {{
            background-image: url('{bg_image}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            color: {text_color};
        }}
        .stApp::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);  /* Dark overlay for better visibility */
            z-index: -1;
        }}
        h1 {{
            text-align: center;
            font-size: 48px;
            font-family: 'Arial', sans-serif;
            color: {text_color};
        }}
        .stTextInput > div > div > input {{
            font-size: 24px;
        }}
        .stRadio > div > label {{
            color: {text_color};
        }}
        .stMetric > div > p {{
            color: {text_color};
        }}
        .stButton > button {{
            background-color: #007bff; 
            color: white;
            font-size: 18px;
            padding: 10px;
            border-radius: 8px;
        }}
        .stButton > button:hover {{
            background-color: #0056b3;
        }}
    </style>
""", unsafe_allow_html=True)

# Centering the title and input box
st.title("🌤 Weather App")

# Unit Toggle with placecard
unit = st.radio("Choose Temperature Unit:", ["Celsius (°C)", "Fahrenheit (°F)"], horizontal=True, key="unit_radio")
unit_param = "metric" if "Celsius" in unit else "imperial"
unit_symbol = "°C" if unit_param == "metric" else "°F"

# API Key
API_KEY = "c9ad69f4ca547728b696660a8056c71d"

# Map selection toggle
use_map = st.checkbox("Use Map to Select City", key="use_map_checkbox")

selected_city = None

if use_map:
    st.subheader("📍 Click on the map to choose a location")
    m = folium.Map(location=[location.latlng[0], location.latlng[1]] if location.ok else [51.5074, -0.1278], zoom_start=5)
    map_data = st_folium(m, height=350, width=700)

    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        geolocator = Nominatim(user_agent="weather-app")
        place = geolocator.reverse((lat, lon), language='en')
        if place:
            selected_city = (
                place.raw.get("address", {}).get("city")
                or place.raw.get("address", {}).get("town")
                or place.raw.get("address", {}).get("village")
            )

    if selected_city:
        city = selected_city
        st.success(f"City detected: {city}")
    else:
        city = None
        st.warning("Click on the map to select a city.")
else:
    city = st.text_input("Or enter City Name:", city_default, placeholder="Enter city (e.g. London)")

if st.button("Get Weather") and city:
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={unit_param}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        pressure = data["main"]["pressure"]
        desc = data["weather"][0]["description"].title()
        icon = data["weather"][0]["icon"]
        weather_id = data["weather"][0]["id"]

        # Weather-based background switch
        if 200 <= weather_id <= 232:
            bg_image = "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1350&q=80"  # thunderstorm
        elif 300 <= weather_id <= 531:
            bg_image = "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?auto=format&fit=crop&w=1350&q=80"  # rain
        elif 600 <= weather_id <= 622:
            bg_image = "https://images.unsplash.com/photo-1518458028785-8fbcd101ebb9?auto=format&fit=crop&w=1350&q=80"  # snow
        elif 701 <= weather_id <= 781:
            bg_image = "https://images.unsplash.com/photo-1524429656589-6633a470097c?auto=format&fit=crop&w=1350&q=80"  # mist
        elif weather_id == 800:
            bg_image = "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1350&q=80"  # clear sky
        elif 801 <= weather_id <= 804:
            bg_image = "https://images.unsplash.com/photo-1503264116251-35a269479413?auto=format&fit=crop&w=1350&q=80"  # cloudy

        st.markdown(f"""
            <style>
                .stApp {{
                    background-image: url('{bg_image}');
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                    color: {text_color};
                }}
            </style>
        """, unsafe_allow_html=True)

        st.image(f"http://openweathermap.org/img/wn/{icon}@2x.png")
        st.subheader(f"Weather in {city.title()}: {desc}")
        st.metric(label="Temperature", value=f"{temp} {unit_symbol}", delta=f"Feels like {feels_like} {unit_symbol}")
        st.markdown(f"💧 **Humidity:** {humidity}%")
        st.markdown(f"🌬 **Wind Speed:** {wind} m/s")
        st.markdown(f"📉 **Pressure:** {pressure} hPa")

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to retrieve weather data: {e}")
