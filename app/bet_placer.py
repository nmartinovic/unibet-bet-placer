async def place_bets(page, bets):
    print("Placing bets...")
    for bet in bets:
        print(f"- {bet['horse_name']} (#{bet['horse_number']}), {bet['bet_type']}, €{bet['amount']}")
        # TODO: Add real Playwright logic to locate runner, select bet type, enter amount, confirm
