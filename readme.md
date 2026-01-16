## Operation Instructions

| Feature | Keywords / Triggers | Example Command |
| --- | --- | --- |
| **Add Item** | add | "Shop add an RTX 5090 for 2500 dollars" |
| **Check Stock** | check, inventory, stock, have, list | "Shop check if we have any thermal paste" |
| **Remove Item** | remove, delete | "Shop remove the broken power supply" |
| **Work Tickets** | ticket, list tickets | "Shop create a ticket to fix the front door lock" |
| **Reminders** | remind, list reminders | "Shop remind me to call the vendor at 4 PM" |
| **Calendar** | Add to calendar, add event to calendar | "Hey Shop, add client coming in at 12pm on friday the 16th of January" |

> **Note: You must say Hey Shop or Shop to activate the systems.**

---

### **Easy way:** Run the **start_shop** script for your Operating System (`.bat` for windows, `.sh` for Ubuntu, other distros not supported).

For Ubuntu make sure you open a terminal in the correct location (inside the main folder) and run:

`chmod +x start_shop.sh`

*If that doesn't work proceed to the manual installation.*

---

### **Backend**

1. Ensure **Ollama** is downloaded from `ollama.com`.
2. Ensure **nodejs** is downloaded.
3. Open your terminal and run: `ollama pull llama3.1`.
4. Keep the terminal open or make sure ollama is running in the background.

In a new terminal window, navigate to the main folder of the program, then:

**For Windows, Run:**
```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```


**For Ubuntu, Run:**
```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py

```

---

### **Frontend**

Open a second terminal and navigate to the main folder of the program, then run:

```bash
cd frontend
npm install
npm run dev

```

The output will normally say **Local: http://localhost:5173**. It will automatically open chrome (make sure it's installed). Allow microphone permission, and it should be running.

---

### **Setting up Google Calendar**

The TriCityBot uses the Google Calendar API to manage shop schedules and repair appointments. Follow these steps to link your shop's Google account.

1. **Create Project:** Go to the Google Cloud Console. Click **New Project** and name it `TriCityBot`.
2. **Enable API:** Search for **"Google Calendar API"** in the top search bar and click **Enable**.
3. **Consent Screen:** Go to **APIs & Services > OAuth consent screen**.
4. **Select External** and click **Create**.
5. **Enter App Details:** Enter an App Name (e.g., TriCityBot) and your email for support/contact info.
6. **Save and Continue** until you reach the **Test Users** screen.
7. **IMPORTANT:** Click **+ ADD USERS** and enter the Gmail address you use for the shop.
8. **Create Keys:** Go to the **Credentials** tab on the left.
9. **OAuth client ID:** Click **+ CREATE CREDENTIALS > OAuth client ID**.
10. **Application type:** Select **Desktop App**.
11. **Download:** Click **Create**, then click **Download JSON**.
12. **Final Step:** Rename the downloaded file to exactly `credentials.json` and move it into the root folder of the TriCityBot project.
