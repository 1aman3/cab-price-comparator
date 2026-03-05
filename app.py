from flask import Flask, render_template, request
import requests

app = Flask(__name__)

GOOGLE_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjQ1YWFkZTg2NTkzMDRiMDRhMTM3OWY5NzlhNzI0OWU1IiwiaCI6Im11cm11cjY0In0="
# ---------------- HOME PAGE ----------------

def get_distance_time(origin, destination):

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    params = {
        "origins": origin,
        "destinations": destination,
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params).json()

    try:
        element = response["rows"][0]["elements"][0]

        if element["status"] != "OK":
            return 5, 15  # fallback distance

        distance = element["distance"]["value"] / 1000
        duration = element["duration"]["value"] / 60

        return distance, duration

    except:
        # fallback if API response fails
        return 5, 15


def calculate_fares(distance):

    fares = {
        "Uber": round(50 + distance * 12),
        "Ola": round(45 + distance * 11),
        "Rapido": round(40 + distance * 10)
    }

    return fares


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/compare", methods=["POST"])
def compare():

    pickup = request.form["pickup"]
    drop = request.form["drop"]

    distance, duration = get_distance_time(pickup, drop)

    fares = calculate_fares(distance)

    links = {
        "Uber": f"https://m.uber.com/ul/?action=setPickup&pickup=my_location&dropoff[formatted_address]={drop}",
        "Ola": f"https://book.olacabs.com/?pickup=my_location&drop_location={drop}",
        "Rapido": "https://rapido.bike/"
    }

    return render_template(
        "results.html",
        fares=fares,
        links=links
    )


if __name__ == "__main__":
    app.run(debug=True)