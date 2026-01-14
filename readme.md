### Operation Instructions

| Feature | Keywords / Triggers | Example Command |
| :--- | :--- | :--- |
| **Add Item** | add | "Shop add an RTX 5090 for 2500 dollars" |
| **Check Stock** | check, inventory, stock, have, list | "Shop check if we have any thermal paste" |
| **Remove Item** | remove, delete | "Shop remove the broken power supply" |
| **Work Tickets** | ticket, list tickets | "Shop create a ticket to fix the front door lock" |
| **Reminders** | remind, list reminders | "Shop remind me to call the vendor at 4 PM" |
| **Calendar** | Add to calendar, add event to calendar | "Hey Shop, add client coming in at 12pm on friday the 16th of January" |
**Note: You must say Hey Shop or Shop to activate the systems.**


**Easy way** 
Run the start_shop script for your Operating System (.bat for windows, .sh for Ubuntu, other distros not supported)
For Ubuntu make sure you open a terminal in the correct location (inside the main folder) and run:  
` chmod +x start_shop.sh `

If that doesn't work proceed to the manual installation

**Backend**
Ensure Ollama is downloaded from ollama.com

Ensure nodejs is downloaded

Open your terminal and run: ` ollama pull llama3.1 `

Keep the terminal open or make sure ollama is running in the background

In a new terminal window, navigate to the main folder of the program, than

**For Windows, Run:**  

` cd backend `  

` python -m venv venv `  

` venv\Scripts\activate `  

` pip install -r requirements.txt `  

` python main.py `  


 **For Ubuntu, Run:**  
 
` cd backend `  

` python3 -m venv venv `  

` source venv/bin/activate `  

` pip install -r requirements.txt `  

` python3 main.py `

**Frontend**
Open a second terminal and navigate to the main folder of the program, than run:  

` cd frontend `  

` npm install `  

` npm run dev `

The output will normally say Local: http://localhost:5173
It will automatically open chrome (make sure it's installed)
Alow microphone permission, and it should be running.


**Setting up Google Calendar**
The TriCityBot uses the Google Calendar API to manage shop schedules and repair appointments. Follow these steps to link your shop's Google account.  

Create Project: Go to the Google Cloud Console. Click New Project and name it TriCityBot.  

Enable API: Search for "Google Calendar API" in the top search bar and click Enable. 

Go to APIs & Services > OAuth consent screen.

Select External and click Create.

Enter an App Name (e.g., TriCityBot) and your email for support/contact info.

Click Save and Continue until you reach the Test Users screen.

IMPORTANT: Click + ADD USERS and enter the Gmail address you use for the shop.  

Create Keys: - Go to the Credentials tab on the left.  

Click + CREATE CREDENTIALS > OAuth client ID.  

Select Application type: Desktop App.  

Click Create, then click Download JSON.  

Rename the downloaded file to exactly credentials.json and move it into the root folder of the TriCityBot project.
