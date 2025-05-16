from playwright.async_api import Page

async def place_bet(page: Page, horse_number: int, bet_type: str, amount: float, mode: str = "simple"):
    print(f"Placing {bet_type} bet on horse #{horse_number} for €{amount} in mode {mode}")

    # Step 1: Select correct bet mode
    mode_label = {
        "simple": "Simple",
        "le_deuzio": "Le Deuzio",
        "le_boulet": "Le Boulet"
    }.get(mode.lower())

    if not mode_label:
        raise ValueError(f"Unsupported bet mode: {mode}")

    try:
        await page.get_by_text(mode_label, exact=True).first.click()
        print(f"✔ Clicked '{mode_label}' mode")
        await page.wait_for_timeout(500)
    except Exception:
        print(f"❌ Failed to click '{mode_label}' mode")
        return

    # Step 2: Locate the runner box
    runner_boxes = page.locator(".runner")
    count = await runner_boxes.count()
    matched_runner = None

    for i in range(count):
        box = runner_boxes.nth(i)
        num_el = box.locator(".number")
        if await num_el.inner_text() == str(horse_number):
            matched_runner = box
            break

    if matched_runner is None:
        print(f"❌ Horse #{horse_number} not found.")
        return

    # Step 3: Click the icon
    if bet_type.lower() == "gagnant":
        icon = matched_runner.locator("i[data-turf-bettype-id='1']")
    elif bet_type.lower() == "place":
        icon = matched_runner.locator("i[data-turf-bettype-id='2']")
    else:
        raise ValueError("Unsupported bet type. Use 'gagnant' or 'place'.")

    await icon.scroll_into_view_if_needed()
    await icon.wait_for(state="visible")
    await icon.click()

    # Step 4: Enter the amount
    stake_input = page.locator("input[name='stake']")
    await stake_input.wait_for()
    await stake_input.fill(str(amount))

    # Step 5: Parier and Confirmer
    await page.locator("span", has_text="Parier").click()
    await page.wait_for_timeout(500)
    await page.locator("span", has_text="Confirmer").click()

    print(f"✅ Bet placed on horse #{horse_number}")