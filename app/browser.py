from playwright.async_api import async_playwright
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
import os
print("✅ UNIBET_USERNAME:", os.getenv("UNIBET_USERNAME"))
print("✅ UNIBET_PASSWORD:", os.getenv("UNIBET_PASSWORD"))


async def launch_browser(headless=True, login=True, username=None, password=None, race_url=None):
    if not username or not password:
        raise ValueError("Username or password not set. Check your .env file.")

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    context = await browser.new_context()
    page = await context.new_page()

    # Step 1: Go to race page
    print("Navigating to race page...")
    await page.goto(race_url)

    # Step 2: Accept cookies
    try:
        print("Checking for cookie banner...")
        await page.wait_for_selector("button:has-text('Accepter')", timeout=5000)
        await page.click("button:has-text('Accepter')")
        print("✔ Cookie banner accepted")
    except:
        print("⚠ No cookie banner found")

    # Step 3: Fill birthdate modal (if shown before login)
    try:
        await page.wait_for_selector("input[name='birthdate']", timeout=5000)
        print("Filling birthdate modal...")
        await page.fill("input[name='birthdate']", "09/04/1987")
        await page.click("button:has-text('Valider')")
        print("✔ Birthday submitted")
    except:
        print("⚠ No birthdate modal found")

    # Step 4: Open login modal
    print("Opening login modal...")
    await page.click("text=Se connecter")

    # Step 5: Fill login form directly (no iframe!)
    try:
        print("Waiting for login fields...")
        await page.wait_for_selector("input[placeholder='Email ou pseudo']", timeout=10000)

        print("Filling login fields...")
        await page.fill("input[placeholder='Email ou pseudo']", username)
        await page.fill("input[placeholder='Mot de passe']", password)

        # Fill birthday before clicking login (this is mandatory)
        try:
            await page.wait_for_selector("input[name='birthday_date']", timeout=3000)
            print("Filling birthday before login...")
            await page.click("input[name='birthday_date']")
            await page.type("input[name='birthday_date']", "09/04/1987", delay=100)
        except:
            print("⚠ No birthday field present in login modal")

        print("Submitting login form...")
        try:
            await page.get_by_role("button", name="Connexion").click()
            print("✔ Clicked Connexion button using role selector")
        except:
            print("⚠ get_by_role failed — trying force click")
            await page.locator("button.btn.btn--large.btn--bold", has_text="Connexion").click(force=True)

        await page.wait_for_timeout(2000)  # Pause for visibility

        # Confirm login
        print("Waiting for login confirmation...")
        try:
            await page.wait_for_selector("text=Mon compte", timeout=10000)
            print("✅ Login successful")
        except:
            print("❌ Login may have failed — 'Mon compte' not found")

    except Exception as e:
        print("❌ Login may have failed:", str(e))

    return browser, context, page