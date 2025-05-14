## 📋 Technical Specification: Unibet Horse Racing Bet Automation

### 🌟 Project Goal
Automate the placement of horse racing bets on [unibet.fr](https://www.unibet.fr/) using Playwright. The script will:
- Accept a race URL and a list of bets
- Log in securely using stored credentials
- Navigate to the specified race page
- Place bets as instructed
- Report success or failure for each bet
- Eventually run autonomously on Railway using scheduled triggers

---

### ✅ What Has Been Accomplished

- ✅ Project structure and Poetry environment set up
- ✅ Playwright installed with Chromium browser support
- ✅ Secure credential loading from `.env` file
- ✅ Script opens race page directly and accepts cookie banner
- ✅ Script handles birthdate verification modal before login
- ✅ Script successfully logs in using:
  - Email/pseudo
  - Password
  - Birthdate (entered before enabling login)
- ✅ Script lands on the race page in a logged-in state
- ✅ Initial stub for bet placement system exists
- ✅ Clear console logs at each major step for debugging
- ✅ Project tracked with Git and hosted on GitHub

---

### 🔨 What’s Left To Do

#### 🔹 Core Functionality
- [ ] Implement DOM logic to:
  - Locate horses by number or name
  - Click bet buttons for `gagnant` / `place`
  - Enter stake amount
  - Submit the bet and verify confirmation
- [ ] Handle race-specific edge cases (e.g., horse not found, odds unavailable)

#### 🔹 Input/Output Enhancements
- [ ] Accept structured input from external JSON or CSV files
- [ ] Save bet results (success/failure, error messages) to local log or file

#### 🔹 Resilience and UX
- [ ] Add retry mechanism for login or DOM lookup failures
- [ ] Add screenshots on error or timeout
- [ ] Improve selector robustness for future DOM changes

#### 🔹 Deployment
- [ ] Dockerize the Playwright script for Railway deployment
- [ ] Add Railway triggers or API endpoints for bet placement
- [ ] Persist logs or status updates (e.g., to SQLite or cloud)

#### 🔹 Security
- [ ] Use encrypted secret management in Railway for credentials

---

### 📊 Tech Stack

| Component          | Tool / Framework             |
|--------------------|-------------------------------|
| Language           | Python 3.11+                  |
| Automation         | Playwright                    |
| Packaging          | Poetry                        |
| Runtime            | Windows 11 + PowerShell       |
| Deployment Target  | Railway                       |
| Secrets Handling   | `.env` via `python-dotenv`    |

---

### 📂 Project Structure

```
unibet-bet-placer/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entrypoint for the script
│   ├── browser.py           # Handles login, cookies, birthdate modal
│   ├── bet_placer.py        # Logic for placing bets
│   └── models.py            # Schema for bet data
├── tests/                   # Optional unit tests
├── .env                     # Stores UNIBET_USERNAME and UNIBET_PASSWORD
├── .gitignore
├── README.md
├── pyproject.toml
└── requirements.txt         # If needed outside Poetry
```

---

### 📄 Input Format (Current)

In-memory Python structure:

```python
bets = [
    {
        "horse_number": 5,
        "horse_name": "Flash Lightning",
        "bet_type": "gagnant",
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

Future plan: support loading `.json` or `.csv`.

---

### 🧭 Script Flow

1. **Startup**
   - Load `.env` for credentials
   - Accept a race URL and structured bets

2. **Login**
   - Navigate to race URL
   - Accept cookie banner
   - Fill login modal (email, password, birthdate)
   - Click Connexion
   - Confirm logged-in state

3. **Place Bets (Planned)**
   - For each bet:
     - Locate correct horse
     - Click corresponding `gagnant` or `place` option
     - Input amount
     - Submit
     - Verify success

4. **Reporting**
   - Print and optionally persist bet results
   - Log any failures (horse not found, button disabled, etc.)

---

### 🛡️ Error Handling Plan

| Scenario                         | Planned Response                   |
|----------------------------------|------------------------------------|
| Login fails                      | Log error, abort or retry          |
| Horse not found                  | Skip and warn                      |
| DOM structure changes            | Save screenshot, raise exception   |
| Bet rejected                     | Capture and log error state        |
| Connection or timeout            | Retry or fail gracefully           |

---

### 💡 Developer Notes

- Use `page.pause()` during dev for visual inspection
- Use `poetry run playwright codegen` to explore selectors
- Run locally with:
  ```bash
  $env:PYTHONPATH = "."
  poetry run python app/main.py
  ```

---

### 📈 Roadmap to Railway Deployment

| Milestone                  | Status     |
|---------------------------|------------|
| Local script working      | ✅ Done     |
| Bets placed via script    | ⏳ In progress |
| Dockerize for Railway     | ⏳ Pending  |
| Secure secrets on Railway | ⏳ Pending  |
| Scheduled or API-based    | ⏳ Pending  |