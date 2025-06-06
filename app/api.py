import os
import traceback
import asyncio
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from app.browser import launch_browser
from app.bet_placer import place_bet
from dotenv import load_dotenv

load_dotenv()

UNIBET_USERNAME = os.getenv("UNIBET_USERNAME")
UNIBET_PASSWORD = os.getenv("UNIBET_PASSWORD")

if not UNIBET_USERNAME or not UNIBET_PASSWORD:
    raise RuntimeError("❌ UNIBET_USERNAME or UNIBET_PASSWORD is not set in the .env file")

router = APIRouter()

class Recommendation(BaseModel):
    horse_number: int
    horse_name: str
    bet_type: str  # "win", "place", "deuzio", "boulet"
    bet_amount: float
    race_id: str

class Summary(BaseModel):
    total_bets: int
    total_bet_amount: float
    win_bets: int
    place_bets: int
    deuzio_bets: int
    timestamp: str
    boulot_bets: Optional[int] = 0

class BetPayload(BaseModel):
    race_url: HttpUrl
    recommendations: List[Recommendation]
    summary: Summary

@router.post("/place-bets")
async def place_bets(request: Request, payload: BetPayload):
    if not payload.recommendations:
        return {"detail": "No recommendations to place."}

    print(f"📬 Received betting payload with {len(payload.recommendations)} recommendations")
    print(f"📍 Navigating to: {payload.race_url}")

    try:
        browser, context, page = await launch_browser(
            headless=True,
            login=True,
            username=UNIBET_USERNAME,
            password=UNIBET_PASSWORD,
            race_url=str(payload.race_url)
        )

        current_mode = None

        for rec in payload.recommendations:
            bet_mode = {
                "win": "simple",
                "place": "simple",
                "deuzio": "le_deuzio",
                "boulet": "le_boulet"
            }.get(rec.bet_type.lower(), "simple")

            actual_bet_type = "gagnant" if rec.bet_type == "win" else "place"

            print(f"📝 Attempting: #{rec.horse_number}, {actual_bet_type}, €{rec.bet_amount}, mode={bet_mode}")

            try:
                await place_bet(
                    page=page,
                    horse_number=rec.horse_number,
                    bet_type=actual_bet_type,
                    amount=rec.bet_amount,
                    mode=bet_mode,
                    current_mode=current_mode
                )
                current_mode = bet_mode
                await asyncio.sleep(3)  # ← Insert pause between bets
            except Exception as e:
                print(f"❌ Failed to place bet on horse #{rec.horse_number}: {e}")

        print("✅ Done placing all bets. Closing browser.")
        await browser.close()

    except Exception as e:
        tb = traceback.format_exc()
        print("❌ Fatal error during bet placement:")
        print(tb)
        raise HTTPException(status_code=500, detail=str(e))

    return {"detail": f"{len(payload.recommendations)} bets attempted."}
