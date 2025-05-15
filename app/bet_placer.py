from playwright.async_api import Page

async def place_bet(page: Page, horse_number: int, bet_type: str, amount: float):
    print(f"Placing {bet_type} bet on horse #{horse_number} for €{amount}")
    # Step 1: Click the “Simple” icon
    try:
        print("✔ Clicked 'Simple' bet mode")
    except Exception:
        print("❌ Failed to click 'Simple' mode – trying fallback")
        await page.get_by_text("Simple").nth(0).click()
        await page.wait_for_timeout(500)  # small delay to allow Gagnant/Place icons to show

# Step 2: Find the correct runner box by horse number
    runner_boxes = page.locator(".runner")  # adjust selector if needed
    count = await runner_boxes.count()

    matched_runner = None
    for i in range(count):
        box = runner_boxes.nth(i)
        num_el = box.locator(".number")
        if await num_el.inner_text() == str(horse_number):
            matched_runner = box
            break

    if matched_runner is None:
        raise ValueError(f"Horse number {horse_number} not found on page")

    # Step 3: Click Gagnant or Place icon inside that runner box
    if bet_type.lower() == "gagnant":
        icon = matched_runner.locator("i[data-turf-bettype-id='1']")
    elif bet_type.lower() == "place":
        icon = matched_runner.locator("i[data-turf-bettype-id='2']")
    else:
        raise ValueError("Unsupported bet type. Use 'gagnant' or 'place'.")

    await icon.click()

    # Step 4: Enter the stake amount
    stake_input = page.locator("input[name='stake']")
    await stake_input.wait_for()
    await stake_input.fill(str(amount))

    # Step 5: Click “Parier”
    await page.locator("span", has_text="Parier").click()
    await page.wait_for_timeout(500)  # short wait for UI to show confirmation modal

    # Step 6: Click “Confirmer”
    await page.locator("span", has_text="Confirmer").click()
    print(f"✅ Bet placed on horse #{horse_number}")