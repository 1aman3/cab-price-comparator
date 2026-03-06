from flask import Flask, render_template, request
import requests
import math

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

    uber = round(50 + (distance * 10), 2)
    ola = round(45 + (distance * 9), 2)
    rapido = round(40 + (distance * 8), 2)

    return {
        "Uber": uber,
        "Ola": ola,
        "Rapido": rapido
    }


# -------- HOME PAGE --------
@app.route("/")
def home():
    return render_template("index.html")


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


if __name__ == "__main__":
    app.run(debug=True)