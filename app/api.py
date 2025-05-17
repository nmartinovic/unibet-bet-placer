import os
import traceback
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from playwright.async_api import async_playwright
from app.bet_placer import place_bet

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
        async with async_playwright() as p:
            print("🎬 Launching Playwright browser...")
            browser = await p.chromium.launch(headless=False, slow_mo=100)
            context = await browser.new_context()
            page = await context.new_page()

            print("🔐 Logging into Unibet...")
            await page.goto("https://www.unibet.fr/")
            await page.get_by_text("Connexion").click()
            await page.locator("#username").fill(UNIBET_USERNAME)
            await page.locator("#password").fill(UNIBET_PASSWORD)
            await page.locator("button[type='submit']").click()
            await page.wait_for_timeout(3000)

            print("🏇 Going to race page...")
            await page.goto(payload.race_url)
            await page.wait_for_timeout(3000)

            for rec in payload.recommendations:
                bet_mode = {
                    "win": "simple",
                    "place": "simple",
                    "deuzio": "le_deuzio",
                    "boulet": "le_boulet"
                }.get(rec.bet_type, "simple")

                actual_bet_type = "gagnant" if rec.bet_type == "win" else "place"

                print(f"📝 Bet: horse #{rec.horse_number}, type: {actual_bet_type}, amount: {rec.bet_amount}, mode: {bet_mode}")
                try:
                    await place_bet(
                        page=page,
                        horse_number=rec.horse_number,
                        bet_type=actual_bet_type,
                        amount=rec.bet_amount,
                        mode=bet_mode
                    )
                except Exception as bet_err:
                    print(f"❌ Bet failed for horse #{rec.horse_number}: {bet_err}")

            print("✅ Done — closing browser.")
            await browser.close()

    except Exception as e:
        tb = traceback.format_exc()
        print("❌ Fatal error:")
        print(tb)
        raise HTTPException(status_code=500, detail=str(e))

    return {"detail": f"{len(payload.recommendations)} bets attempted."}
