**Operation instructions**

Add Item	     .       add	                                        .             "Add an RTX 5090 for 2500 dollars."
Check Stock    .      check, inventory, stock, have, list	          .            "Check if we have any thermal paste."
Remove Item	   .       remove, delete	                              .            "Remove the broken power supply."
Work Tickets	 .       ticket	                                      .            "Create a ticket to fix the front door lock."
Reminders      .      	remind	                                    .              "Remind me to call the vendor at 4 PM." (note, this is passive for now, you would have to ask "list my reminders)


**Easy way**
Run the start_shop script for your Operating System (.bat for windows, .sh for Ubuntu, other distros not supported)

If that doesn't work proceed to the manual installation

**Backend**
Ensure Ollama is downloaded from ollama.com

Ensure nodejs is downloaded

Open your terminal and run: ollama pull llama3.1

Keep the terminal open or make sure ollama is running in the background

In a new terminal window, navigate to the main folder of the program, than

For Windows, Run: 
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py 

For Ubuntu, Run:
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py

**Frontend**
Open a second terminal and navigate to the main folder of the program, than run
cd frontend
npm install
npm run dev

The output will normally say Local: http://localhost:5173
Run it in chrome (best for this program without extra plugins)
Alow microphone permission, and it should be running.
