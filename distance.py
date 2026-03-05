import requests

API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjQ1YWFkZTg2NTkzMDRiMDRhMTM3OWY5NzlhNzI0OWU1IiwiaCI6Im11cm11cjY0In0="

def get_distance(start_lon, start_lat, end_lon, end_lat):

    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            [start_lon, start_lat],
            [end_lon, end_lat]
        ]
    }

    response = requests.post(url, json=body, headers=headers)

    data = response.json()

    distance = data["routes"][0]["summary"]["distance"]
    duration = data["routes"][0]["summary"]["duration"]

    return distance, duration