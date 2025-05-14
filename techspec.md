## 📋 Technical Specification: Unibet Horse Racing Bet Automation

### 🌟 Project Goal

Automate the placement of horse racing bets on [unibet.fr](https://www.unibet.fr/) using Playwright. The script will:

* Accept a race URL and list of bets
* Log in with secure credentials
* Navigate to the specified race page
* Place each bet as instructed
* Confirm success or report any errors

---

### 📊 Tech Stack

| Component           | Choice                   |
| ------------------- | ------------------------ |
| Scripting Lang      | Python 3.11+             |
| Automation Tool     | Playwright               |
| OS / Shell          | Windows 11 w/ PowerShell |
| Package Manager     | Poetry                   |
| Deployment (future) | Railway                  |
| Secrets Handling    | .env via python-dotenv   |
| Output Format       | Console logs (for now)   |

---

### 📂 Project Structure

```
unibet-bet-placer/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entrypoint for the script
│   ├── browser.py           # Sets up Playwright context and login
│   ├── bet_placer.py        # Core logic for interpreting and placing bets
│   └── models.py            # Bet dataclass / schema definitions
├── tests/                   # Optional unit/integration tests
├── .env                     # Stores UNIBET_USERNAME and UNIBET_PASSWORD
├── .gitignore
├── README.md
├── pyproject.toml
└── requirements.txt         # If not using poetry
```

---

### 📌 .env Format

```
UNIBET_USERNAME=your_email_here
UNIBET_PASSWORD=your_password_here
```

---

### 📄 Input Format (Initial Version)

Use a Python list of dictionaries. Later versions may support JSON or CSV.

```python
bets = [
    {
        "horse_number": 5,
        "horse_name": "Flash Lightning",
        "bet_type": "gagnant",  # or "place"
        "amount": 2.0
    },
    {
        "horse_number": 3,
        "horse_name": "Midnight Star",
        "bet_type": "place",
        "amount": 1.5
    }
]
```

---

### ⟳ Script Flow

1. **Startup**

   * Load `.env` for credentials
   * Accept command-line args or hardcoded `url` + `bets` for now

2. **Login**

   * Launch browser (visible)
   * Go to login page
   * Fill in credentials
   * Check for success (e.g., profile avatar or account name)

3. **Navigate to Race Page**

   * Go to provided `race_url`

4. **Place Bets**

   * For each bet:

     * Locate horse by number or name
     * Select bet type (`gagnant`, `place`)
     * Enter amount
     * Confirm bet
     * Check for errors or rejection

5. **Report**

   * Print success/failure of each bet
   * Log rejected bets and possible causes (e.g., market closed)

---

### 🧑‍🧬 Future Features (Planned for Later)

* Retry login or re-authentication if session expires
* Support JSON or CSV input formats
* Add complex bets: couplé, trio, etc.
* Error logging with email or webhook notification
* Headless mode toggle via CLI flag
* Deployment via Railway with a scheduler

---

### 🛡️ Error Handling

| Scenario                  | Response                          |
| ------------------------- | --------------------------------- |
| Login failure             | Retry or abort with message       |
| Horse not found           | Warn and skip                     |
| Bet rejected (odds/limit) | Log full context and skip         |
| Site structure changes    | Raise fatal error with screenshot |

---

### ✅ Local Dev Tips

* Run with: `poetry run python app/main.py`
* Use Playwright’s dev tools: `page.pause()` for debugging
* Use `playwright codegen` to prototype interactions quickly
