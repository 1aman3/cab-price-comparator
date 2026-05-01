from flask import Flask, render_template, request, jsonify
import requests
import math
import random
from datetime import datetime

app = Flask(__name__)

GOOGLE_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjQ1YWFkZTg2NTkzMDRiMDRhMTM3OWY5NzlhNzI0OWU1IiwiaCI6Im11cm11cjY0In0="
# ---------------- HOME PAGE ----------------

def get_coordinates(place):
    url = f"https://nominatim.openstreetmap.org/search?q={place}&format=json"

    headers = {
        "User-Agent": "cab-price-comparator"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    if len(data) == 0:
        return None

    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])

    return lat, lon


# -------- DISTANCE CALCULATION --------
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c

    return round(distance, 2)


# -------- FARE ENGINE --------
def calculate_fares(distance):
    fares = {}

    # Get current hour
    hour = datetime.now().hour

    # Traffic factor
    if 8 <= hour <= 11 or 17 <= hour <= 21:
        traffic_factor = 1.25
    elif 22 <= hour or hour <= 6:
        traffic_factor = 0.9
    else:
        traffic_factor = 1.0

    # Surge factor
    surge_factor = random.uniform(0.95, 1.35)

    # ------------------------
    # Uber
    # ------------------------

    uber_base = 50
    uber_per_km = 12
    uber_minimum = 80

    uber_fare = uber_base + (distance * uber_per_km)

    uber_fare *= traffic_factor
    uber_fare *= surge_factor

    uber_fare += random.uniform(-5, 5)

    uber_fare = max(uber_fare, uber_minimum)

    fares["Uber"] = round(uber_fare)

    # ------------------------
    # Ola
    # ------------------------

    ola_base = 45
    ola_per_km = 11
    ola_minimum = 75

    ola_fare = ola_base + (distance * ola_per_km)

    ola_fare *= traffic_factor
    ola_fare *= surge_factor

    ola_fare += random.uniform(-5, 5)

    ola_fare = max(ola_fare, ola_minimum)

    fares["Ola"] = round(ola_fare)

    # ------------------------
    # Rapido
    # ------------------------

    rapido_base = 25
    rapido_per_km = 8
    rapido_minimum = 40

    rapido_fare = rapido_base + (distance * rapido_per_km)

    rapido_fare *= traffic_factor
    rapido_fare *= surge_factor

    rapido_fare += random.uniform(-5, 5)

    rapido_fare = max(rapido_fare, rapido_minimum)

    fares["Rapido"] = round(rapido_fare)

    return fares

# -------- HOME PAGE --------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/suggest")
def suggest():

    query = request.args.get("q")

    if not query:
        return jsonify([])

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": query,
        "format": "json",
        "limit": 5,
        "countrycodes": "in"
    }

    headers = {
        "User-Agent": "CabCompareApp"
    }

    response = requests.get(url, params=params, headers=headers)

    data = response.json()

    suggestions = []

    for place in data:

        suggestions.append({
            "name": place["display_name"],
            "lat": place["lat"],
            "lon": place["lon"]
        })

    return jsonify(suggestions)
# -------- SEARCH ROUTE --------
@app.route("/search", methods=["POST"])
def search():

    source = request.form.get("source")
    destination = request.form.get("destination")

    source_coords = get_coordinates(source)
    dest_coords = get_coordinates(destination)

    if source_coords is None or dest_coords is None:
        return render_template("results.html", error="Location not found")

    lat1, lon1 = source_coords
    lat2, lon2 = dest_coords

    distance = calculate_distance(lat1, lon1, lat2, lon2)

    fares = calculate_fares(distance)

    links = {
        "Uber": f"https://m.uber.com/ul/?action=setPickup&pickup=my_location&dropoff[formatted_address]={destination}",
        "Ola": "https://book.olacabs.com/",
        "Rapido": "https://rapido.bike/"
    }

    return render_template(
        "results.html",
        source=source,
        destination=destination,
        distance=distance,
        fares=fares,
        links=links
    )



   
   
@app.route("/reverse_geocode")
def reverse_geocode():

    lat = request.args.get("lat")
    lon = request.args.get("lon")

    url = "https://nominatim.openstreetmap.org/reverse"

    params = {
        "lat": lat,
        "lon": lon,
        "format": "json"
    }

    headers = {
        "User-Agent": "CabCompareApp"
    }

    response = requests.get(url, params=params, headers=headers)

    data = response.json()

    name = data.get("display_name", "Current Location")

    return jsonify({"name": name})

if __name__ == "__main__":
    app.run(debug=True)