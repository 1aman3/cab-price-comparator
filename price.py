def calculate_fares(distance_meters, duration_seconds):

    distance_km = distance_meters / 1000
    time_min = duration_seconds / 60

    uber = 50 + (distance_km * 10) + (time_min * 1)
    ola = 40 + (distance_km * 9) + (time_min * 1.2)
    rapido = 30 + (distance_km * 8) + (time_min * 1)

    return {
        "Uber": round(uber, 2),
        "Ola": round(ola, 2),
        "Rapido": round(rapido, 2)
    }