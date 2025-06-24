from playwright.async_api import async_playwright
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
import os
import re
print("✅ UNIBET_USERNAME:", os.getenv("UNIBET_USERNAME"))
print("✅ UNIBET_PASSWORD:", os.getenv("UNIBET_PASSWORD"))


async def launch_browser(headless=True, login=True, username=None, password=None, race_url=None):
    if not username or password:
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


async def get_account_balance(page) -> float:
    """
    Extract account balance from the page after login.
    
    Returns:
        float: Account balance in euros
    """
    try:
        print("🔍 Looking for account balance...")
        
        # Wait for balance element to be visible
        balance_selector = "span.balance-real-value"
        await page.wait_for_selector(balance_selector, timeout=10000)
        
        # Get the balance text
        balance_text = await page.inner_text(balance_selector)
        print(f"📊 Raw balance text: '{balance_text}'")
        
        # Parse the balance (handle French number format: "74,20 €")
        # Remove currency symbol and convert comma to dot
        balance_clean = re.sub(r'[€\s]', '', balance_text).replace(',', '.')
        balance_amount = float(balance_clean)
        
        print(f"💰 Account balance: €{balance_amount}")
        return balance_amount
        
    except Exception as e:
        print(f"❌ Failed to get account balance: {e}")
        # Try alternative selectors as fallback
        try:
            # Look for any element containing balance info
            balance_elements = await page.query_selector_all("[class*='balance']")
            for elem in balance_elements:
                text = await elem.inner_text()
                if '€' in text and any(char.isdigit() for char in text):
                    print(f"🔍 Found potential balance: '{text}'")
                    # Try to extract number
                    match = re.search(r'(\d+(?:,\d+)?)\s*€', text)
                    if match:
                        balance_clean = match.group(1).replace(',', '.')
                        balance_amount = float(balance_clean)
                        print(f"💰 Extracted balance: €{balance_amount}")
                        return balance_amount
        except Exception as fallback_error:
            print(f"❌ Fallback balance extraction failed: {fallback_error}")
        
        raise Exception(f"Could not extract account balance: {e}")


def calculate_bet_amount(balance: float, percentage: float) -> int:
    """
    Calculate bet amount based on balance and percentage.
    
    Args:
        balance: Account balance in euros
        percentage: Bet percentage (e.g., 0.05 for 5%)
    
    Returns:
        int: Bet amount in euros (minimum 1, rounded to nearest euro)
    """
    if percentage <= 0:
        return 1  # Minimum bet
    
    # Calculate percentage of balance (percentage is already decimal, no need to divide by 100)
    raw_amount = percentage * balance
    
    # Round to nearest euro, minimum 1
    bet_amount = max(1, round(raw_amount))
    
    print(f"💡 {percentage:.3f} (={percentage*100:.1f}%) of €{balance:.2f} = €{raw_amount:.2f} → €{bet_amount}")
    return bet_amount