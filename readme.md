### Operation Instructions

| Feature | Keywords / Triggers | Example Command |
| :--- | :--- | :--- |
| **Add Item** | add | "Shop add an RTX 5090 for 2500 dollars" |
| **Check Stock** | check, inventory, stock, have, list | "Shop check if we have any thermal paste" |
| **Remove Item** | remove, delete | "Shop remove the broken power supply" |
| **Work Tickets** | ticket, list tickets | "Shop create a ticket to fix the front door lock" |
| **Reminders** | remind, list reminders | "Shop remind me to call the vendor at 4 PM" |
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
