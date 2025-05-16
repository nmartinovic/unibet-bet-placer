from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from app.browser import launch_browser
from app.bet_placer import place_bet
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()

class Recommendation(BaseModel):
    horse_number: int
    horse_name: str
    bet_type: str  # 'win', 'place', 'deuzio', 'boulet'
    bet_amount: float
    race_id: str

class Summary(BaseModel):
    total_bets: int
    total_bet_amount: float
    win_bets: int
    place_bets: int
    deuzio_bets: int
    boulot_bets: Optional[int] = 0 # ← Add this line
    timestamp: str

class BetRequest(BaseModel):
    race_url: str
    recommendations: List[Recommendation]
    summary: Summary

@app.post("/place-bets")
async def place_bets(request: BetRequest):
    try:
        browser, context, page = await launch_browser(headless=False, login=True)
        await page.goto(request.race_url, timeout=60000)

        for rec in request.recommendations:
            await place_bet(
                page=page,
                horse_number=rec.horse_number,
                bet_type=rec.bet_type,
                amount=rec.bet_amount
            )

        await browser.close()
        return {"status": "success", "message": f"{len(request.recommendations)} bets placed"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

