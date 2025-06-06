import asyncio
import requests
import json

payload = {
    "race_url": "https://www.unibet.fr/turf/race/17-05-2025-R4-C10-lyon-parilly-prix-dabrest.html",
    'recommendations': [
                      {'bet_amount': 1,
                      'bet_type': 'deuzio',
                      'horse_name': 'KSAR LUDOIS',
                      'horse_number': 5,
                      'race_id': 'race_data'}],
 'summary': {'boulot_bets': 0,
             'deuzio_bets': 1,
             'place_bets': 0,
             'timestamp': '2025-05-17T15:29:10.533183',
             'total_bet_amount': 10.3,
             'total_bets': 2,
             'win_bets': 2}}

def run_post():
    print("🚀 Sending request to FastAPI server...")
    response = requests.post("http://127.0.0.1:5173/place-bets", json=payload, timeout=60)
    print(f"📡 Status: {response.status_code}")
    print(f"📨 Response: {response.text}")

if __name__ == "__main__":
    run_post()
