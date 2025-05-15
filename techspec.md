## 📋 Technical Specification: Unibet Horse Racing Bet Automation

### 🌟 Project Goal
Automate the placement of horse racing bets on [unibet.fr](https://www.unibet.fr/) using Playwright. The script:
- Accepts a race URL and list of bets
- Logs in using secure credentials
- Navigates to the race page
- Places each bet by selecting Gagnant or Place, entering stake, confirming
- Supports multiple bets per race with delay between each
- Will eventually run on Railway as a containerized scheduled app

---

### ✅ What’s Done

#### 🔒 Login Flow
- Navigates to race URL directly
- Accepts cookie banner
- Fills and submits login modal (email, password, birthdate)
- Handles visibility issues and retries on modal state

#### 🐎 Bet Placement Flow
- Clicks “Simple” bet mode once per race
- Locates correct horse via `.runner .number`
- Selects either Gagnant or Place icon (based on input)
- Enters amount into visible input
- Clicks “Parier” and then “Confirmer”
- Adds a pause between bets for UI reset
- Logs each successful bet

#### ⚙️ Tooling & Architecture
- FastAPI debug server (already present)
- Scraper scheduler in place
- Railway-ready Docker setup
- Project tracked in Git with clean file structure

---

### 🛠 What’s Next

| Feature                      | Status   |
|------------------------------|----------|
| Error handling (odds changed, bet rejected) | ⏳ In progress |
| Log bets to SQLite or .csv   | ⏳ Planned |
| Accept external JSON input   | ⏳ Planned |
| Add support for combo bets   | ⏳ Future |
| Trigger via FastAPI or CLI   | ⏳ Future |
| Deploy to Railway            | ⏳ Future |

---

### 📂 File Structure

```
nmartinovic-horse-bets/
├── app/
│   ├── main.py              # Entrypoint for betting
│   ├── bet_placer.py        # Logic to select/check horse and place bet
│   ├── browser.py           # Login automation logic
├── scraper/                 # Original scraping engine
├── data/                    # (Runtime) SQLite DB mount for Railway
├── pyproject.toml
├── Dockerfile
└── railway.toml
```

---

### 📄 Sample Input Format

```python
bets = [
    {"horse_number": 9, "bet_type": "gagnant", "amount": 2.0},
    {"horse_number": 9, "bet_type": "place",   "amount": 1.0}
]
```

---

### 🔁 Script Flow

1. Launch browser (headless optional)
2. Login using credentials in `.env`
3. Navigate to given race page
4. Click “Simple”
5. For each bet:
   - Locate runner box by horse number
   - Click Gagnant or Place icon
   - Input stake amount
   - Submit and confirm bet
   - Wait 3 seconds
6. Close browser

---

### 🛡️ Error Handling Plan (Next Iteration)

| Case                             | Plan                                  |
|----------------------------------|---------------------------------------|
| Element not found (DOM shift)    | Screenshot + fail gracefully          |
| Bet rejected (odds changed)      | Log to file and skip next bet         |
| Login fails                      | Abort run or retry once               |
| Stake entry fails                | Retry once after delay                |

---

### 🧪 Dev Tips

- Use `page.pause()` for manual debugging
- Use `get_by_role()` or robust locators with `.scroll_into_view_if_needed()`
- Watch for false negatives: hidden elements ≠ missing

---

### ✅ Local Run

```bash
$env:PYTHONPATH = "."
poetry run python app/main.py
```

---

Ready for Railway deployment, logging, or trigger enhancements when you are.