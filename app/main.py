from dotenv import load_dotenv
import os
from app.browser import launch_browser
from app.bet_placer import place_bets

# Load environment variables
load_dotenv()

UNIBET_USERNAME = os.getenv("UNIBET_USERNAME")
UNIBET_PASSWORD = os.getenv("UNIBET_PASSWORD")

# Example race URL and bets
RACE_URL = "https://www.unibet.fr/turf/race/14-05-2025-R8-C8-valparaiso-prix-golden-victory.html"

bets = [
    {
        "horse_number": 5,
        "horse_name": "Flash Lightning",
        "bet_type": "gagnant",
        "amount": 2.0
    },
    {
        "horse_number": 3,
        "horse_name": "Midnight Star",
        "bet_type": "place",
        "amount": 1.5
    }
]

async def main():
    browser, context, page = await launch_browser(
        headless=False,
        login=True,
        username=UNIBET_USERNAME,
        password=UNIBET_PASSWORD,
        race_url=RACE_URL
    )

    # You’re already on the race page after login now
    await place_bets(page, bets)

    await browser.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
