import requests

payload = {
    "race_url": "https://www.unibet.fr/turf/race/17-05-2025-R2-C2-wolvega-prix-local-hero.html",
    "recommendations": [
        {
            "horse_number": 2,
            "horse_name": "GOLDEN DE PAME",
            "bet_type": "win",
            "bet_amount": 2,
            "race_id": "race_data"
        }
    ],
    "summary": {
        "total_bets": 1,
        "total_bet_amount": 2.0,
        "win_bets": 1,
        "place_bets": 0,
        "deuzio_bets": 0,
        "boulot_bets": 0,
        "timestamp": "2025-05-16T22:27:14.795620"
    }
}

response = requests.post("http://127.0.0.1:5173/place-bets", json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
