import os
import traceback
import asyncio
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from app.browser import launch_browser, get_account_balance, calculate_bet_amount
from app.bet_placer import place_bet
from dotenv import load_dotenv

# Load environment variables at module level - try multiple approaches
load_dotenv()
load_dotenv(dotenv_path=".env")
load_dotenv(dotenv_path="../.env")

UNIBET_USERNAME = os.getenv("UNIBET_USERNAME")
UNIBET_PASSWORD = os.getenv("UNIBET_PASSWORD")

print(f"🔍 DEBUG - api.py loaded credentials:")
print(f"   UNIBET_USERNAME: {UNIBET_USERNAME}")
print(f"   UNIBET_PASSWORD: {'***' if UNIBET_PASSWORD else 'NOT SET'}")

if not UNIBET_USERNAME or not UNIBET_PASSWORD:
    raise RuntimeError("❌ UNIBET_USERNAME or UNIBET_PASSWORD is not set in the .env file")

router = APIRouter()

class Recommendation(BaseModel):
    horse_number: Optional[int] = None      # Will extract from race data if missing
    horse_name: str
    bet_type: str  # "win", "place", "deuzio", "boulet"
    bet_percentage: Optional[float] = None   # Primary field
    bet_amount: Optional[float] = None       # Alternative field name
    race_id: Optional[str] = None
    
    # Optional fields that can be ignored
    confidence: Optional[float] = None
    edge: Optional[float] = None
    estimated_place_odds: Optional[float] = None
    kelly_fraction: Optional[float] = None
    strategy: Optional[str] = None
    win_odds: Optional[float] = None
    
    def get_bet_percentage(self) -> float:
        """Get bet percentage from either field name"""
        return self.bet_percentage or self.bet_amount or 0.0

class Summary(BaseModel):
    boulot_bets: Optional[int] = 0
    total_amount: Optional[float] = 0
    total_bet_amount: Optional[float] = 0  # Keep original field name for compatibility
    win_bets: Optional[int] = 0
    place_bets: Optional[int] = 0
    deuzio_bets: Optional[int] = 0
    timestamp: str

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

        # Get account balance after login
        print("💰 Getting account balance...")
        account_balance = await get_account_balance(page)
        print(f"💰 Account balance: €{account_balance}")

        current_mode = None
        placed_bets = []
        total_bet_amount = 0.0

        for rec in payload.recommendations:
            # Get bet percentage from either field
            bet_percentage = rec.get_bet_percentage()
            
            # Check if horse_number is missing
            if not rec.horse_number:
                print(f"❌ Missing horse_number for {rec.horse_name} - skipping bet")
                placed_bets.append({
                    "horse_name": rec.horse_name,
                    "bet_type": rec.bet_type,
                    "bet_percentage": bet_percentage,
                    "status": "error",
                    "error": "Missing horse_number"
                })
                continue
            
            # Calculate actual bet amount from percentage
            bet_amount = calculate_bet_amount(account_balance, bet_percentage)
            total_bet_amount += bet_amount

            bet_mode = {
                "win": "simple",
                "place": "simple",
                "deuzio": "le_deuzio",
                "boulet": "le_boulet"
            }.get(rec.bet_type.lower(), "simple")

            actual_bet_type = "gagnant" if rec.bet_type == "win" else "place"

            print(f"📝 Attempting: #{rec.horse_number} ({rec.horse_name}), {actual_bet_type}, €{bet_amount} ({rec.bet_percentage}%), mode={bet_mode}")

            try:
                success = await place_bet(
                    page=page,
                    horse_number=rec.horse_number,
                    bet_type=actual_bet_type,
                    amount=bet_amount,
                    mode=bet_mode,
                    current_mode=current_mode
                )
                
                if success:
                    placed_bets.append({
                        "horse_number": rec.horse_number,
                        "horse_name": rec.horse_name,
                        "bet_type": rec.bet_type,
                        "bet_percentage": rec.bet_percentage,
                        "bet_amount": bet_amount,
                        "status": "success"
                    })
                    print(f"✅ Successfully placed €{bet_amount} bet on #{rec.horse_number}")
                else:
                    placed_bets.append({
                        "horse_number": rec.horse_number,
                        "horse_name": rec.horse_name,
                        "bet_type": rec.bet_type,
                        "bet_percentage": rec.bet_percentage,
                        "bet_amount": bet_amount,
                        "status": "failed"
                    })
                    print(f"❌ Failed to place bet on #{rec.horse_number}")
                
                current_mode = bet_mode
                await asyncio.sleep(3)  # Pause between bets
                
            except Exception as e:
                print(f"❌ Failed to place bet on horse #{rec.horse_number}: {e}")
                placed_bets.append({
                    "horse_number": rec.horse_number,
                    "horse_name": rec.horse_name,
                    "bet_type": rec.bet_type,
                    "bet_percentage": rec.bet_percentage,
                    "bet_amount": bet_amount,
                    "status": "error",
                    "error": str(e)
                })

        print("✅ Done placing all bets. Closing browser.")
        await browser.close()

        # Return detailed results
        successful_bets = len([bet for bet in placed_bets if bet["status"] == "success"])
        failed_bets = len([bet for bet in placed_bets if bet["status"] != "success"])

        return {
            "detail": f"Betting completed: {successful_bets} successful, {failed_bets} failed",
            "account_balance": account_balance,
            "total_bet_amount": total_bet_amount,
            "placed_bets": placed_bets,
            "summary": {
                "total_attempts": len(payload.recommendations),
                "successful_bets": successful_bets,
                "failed_bets": failed_bets,
                "total_amount_bet": total_bet_amount
            }
        }

    except Exception as e:
        tb = traceback.format_exc()
        print("❌ Fatal error during bet placement:")
        print(tb)
        raise HTTPException(status_code=500, detail=str(e))