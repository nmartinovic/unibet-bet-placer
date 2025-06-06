from playwright.async_api import Page, TimeoutError as PlaywrightTimeout
import asyncio

async def place_bet(
    page: Page,
    horse_number: int,
    bet_type: str,
    amount: float,
    mode: str = "simple",
    current_mode: str = None,
) -> bool:
    print(f"📝 Attempting: #{horse_number}, {bet_type}, €{amount}, mode={mode}")

    # Step 1: Select correct bet mode only if different from current
    mode_labels = {
        "simple": "Simple",
        "le_deuzio": "Le Deuzio",
        "le_boulet": "Le Boulet",
    }

    mode_label = mode_labels.get(mode.lower())
    if not mode_label:
        raise ValueError(f"Unsupported bet mode: {mode}")

    if current_mode != mode:
        try:
            await page.get_by_text(mode_label, exact=True).first.click()
            print(f"✔ Clicked '{mode_label}' mode")
            await page.wait_for_timeout(500)
        except Exception as e:
            print(f"❌ Failed to click '{mode_label}' mode: {e}")
            return False

    # Step 2: Locate the runner box
    runner_boxes = page.locator(".runner")
    count = await runner_boxes.count()
    matched_runner = None

    for i in range(count):
        box = runner_boxes.nth(i)
        num_el = box.locator(".number")
        try:
            if await num_el.inner_text() == str(horse_number):
                matched_runner = box
                break
        except Exception:
            continue

    if matched_runner is None:
        print(f"❌ Horse #{horse_number} not found.")
        return False

    # Step 3: Click the correct icon for the bet type
    try:
        if mode == "le_deuzio":
            icon = matched_runner.locator("div.betchoice.standard.no-formula i.bet.base").first
        elif mode == "le_boulet":
            icon = matched_runner.locator(".betchoice.field i").nth(1)
        else:
            if bet_type.lower() == "gagnant":
                icon = matched_runner.locator("i[data-turf-bettype-id='1']")
            elif bet_type.lower() == "place":
                icon = matched_runner.locator("i[data-turf-bettype-id='2']")
            else:
                raise ValueError("Unsupported bet type. Use 'gagnant' or 'place'.")

        await icon.scroll_into_view_if_needed()
        await icon.wait_for(state="visible", timeout=5000)
        await icon.click()
    except Exception as e:
        print(f"❌ Failed to click bet icon: {e}")
        return False

    # Step 4: Fill in the stake amount
    try:
        stake_input = page.locator("input[name='stake']")
        await stake_input.wait_for(timeout=5000)
        await stake_input.fill(str(amount))
    except Exception as e:
        print(f"❌ Failed to enter stake: {e}")
        return False

    # Step 5: Confirm the bet
    try:
        await page.locator("span", has_text="Parier").click()
        await page.wait_for_timeout(500)

        confirm_button = page.locator("#turf_betslip_confirm")
        await confirm_button.wait_for(timeout=5000)
        await confirm_button.click()

        print(f"✅ Bet placed on horse #{horse_number}")
    except PlaywrightTimeout:
        print("❌ Confirm button not found in time")
        return False
    except Exception as e:
        print(f"❌ Failed to finalize bet: {e}")
        return False

    # Step 6: Wait 3 seconds before next bet
    await asyncio.sleep(3)
    return True
