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
