import sys
import subprocess
import os
import json
import sqlite3
import time
import pickle
import wave
import struct
from datetime import datetime, timedelta

# --- 1. BOOTSTRAPPER & ABSOLUTE PATHS ---
# This ensures credentials.json and shop.db are found regardless of terminal location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_PATH = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')
DB_PATH = os.path.join(BASE_DIR, 'shop.db')
SPEAKER_WAV = os.path.join(BASE_DIR, "speaker.wav")

REQUIRED_PACKAGES = {
    "ollama": "ollama",
    "google-api-python-client": "googleapiclient",
    "google-auth-oauthlib": "google_auth_oauthlib",
    "tavily-python": "tavily",
    "SpeechRecognition": "speech_recognition",
    "sounddevice": "sounddevice",
    "soundfile": "soundfile",
    "colorama": "colorama",
    "pyttsx3": "pyttsx3"
}

def install_package(package):
    print(f"[System] Installing missing package: {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception as e:
        print(f"[Critical] Failed to install {package}: {e}")

for package, import_name in REQUIRED_PACKAGES.items():
    try:
        __import__(import_name)
    except ImportError:
        install_package(package)

# --- IMPORTS ---
import ollama
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import pyttsx3
from colorama import init, Fore, Style
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from tavily import TavilyClient

init(autoreset=True)
SCOPES = ['https://www.googleapis.com/auth/calendar']

# --- 2. AUDIO ENGINE ---
class AudioEngine:
    def __init__(self):
        self.use_xtts = False
        self.fallback = pyttsx3.init()
        self.fallback.setProperty('rate', 150)
        
        try:
            from TTS.api import TTS
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"{Fore.CYAN}[System] Loading Neural TTS...{Style.RESET_ALL}")
            self.tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
            self.use_xtts = True
        except Exception as e:
            print(f"{Fore.YELLOW}[Audio] Neural TTS unavailable (using system fallback).{Style.RESET_ALL}")

    def speak(self, text):
        if not text: return
        if self.use_xtts and os.path.exists(SPEAKER_WAV):
            try:
                temp = os.path.join(BASE_DIR, "temp_speech.wav")
                self.tts_model.tts_to_file(text=text, speaker_wav=SPEAKER_WAV, language="en", file_path=temp)
                data, fs = sf.read(temp)
                sd.play(data, fs)
                sd.wait()
                os.remove(temp)
                return
            except: pass
        self.fallback.say(text)
        self.fallback.runAndWait()

# --- 3. CORE SHOP OS CLASS ---
class ShopOS:
    def __init__(self, audio_engine):
        self.audio = audio_engine
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        # HARDCODED TAVILY KEY
        self.tavily = TavilyClient(api_key="tvly-dev-placeholder") # Replace with your actual key here

    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS inventory (name TEXT PRIMARY KEY, price REAL, quantity INTEGER DEFAULT 1)')
        cur.execute('CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, status TEXT DEFAULT "OPEN")')
        self.conn.commit()

    def _get_calendar_service(self):
        creds = None
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'rb') as token: creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDS_PATH): return None
                flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, 'wb') as token: pickle.dump(creds, token)
        return build('calendar', 'v3', credentials=creds)

    # --- SYSTEM TOOLS ---
    def daily_briefing(self):
        service = self._get_calendar_service()
        if not service: return "Calendar not authorized."
        now = datetime.utcnow()
        start = datetime(now.year, now.month, now.day, 0, 0, 0).isoformat() + 'Z'
        end = datetime(now.year, now.month, now.day, 23, 59, 59).isoformat() + 'Z'
        events = service.events().list(calendarId='primary', timeMin=start, timeMax=end, singleEvents=True, orderBy='startTime').execute()
        items = events.get('items', [])
        if not items: return "Your schedule is clear today."
        brief = "Today's schedule: "
        for e in items:
            t = datetime.fromisoformat(e['start'].get('dateTime', e['start'].get('date')).replace('Z', ''))
            brief += f"At {t.strftime('%I:%M %p')}, {e['summary']}. "
        return brief

    def inventory_add(self, name, price, qty):
        name = name.upper().strip()
        self.conn.execute("INSERT INTO inventory (name, price, quantity) VALUES (?, ?, ?) ON CONFLICT(name) DO UPDATE SET quantity = inventory.quantity + ?, price = ?", (name, float(price), int(qty), int(qty), float(price)))
        self.conn.commit()
        return f"Added {qty} {name} to stock."

    def inventory_check(self, term):
        cur = self.conn.cursor()
        if term and term.lower() != "none":
            res = cur.execute("SELECT * FROM inventory WHERE name LIKE ?", (f"%{term.upper()}%",)).fetchall()
        else:
            res = cur.execute("SELECT * FROM inventory").fetchall()
        return ". ".join([f"{r['name']} (${r['price']:.2f}, Qty: {r['quantity']})" for r in res]) if res else "No inventory found."

    def create_ticket(self, desc):
        self.conn.execute("INSERT INTO tickets (description) VALUES (?)", (desc,))
        self.conn.commit()
        return "Ticket created."

    def list_tickets(self):
        res = self.conn.execute("SELECT * FROM tickets WHERE status='OPEN'").fetchall()
        return ". ".join([f"#{r['id']} {r['description']}" for r in res]) if res else "No open tickets."

    def google_calendar(self, summary, time_str):
        service = self._get_calendar_service()
        if not service: return "Calendar auth failed."
        event = {'summary': summary, 'start': {'dateTime': f"{time_str}:00", 'timeZone': 'MST'}, 'end': {'dateTime': f"{time_str}:00", 'timeZone': 'MST'}}
        service.events().insert(calendarId='primary', body=event).execute()
        return f"Scheduled {summary}."

    def research(self, query):
        if not self.tavily: return "Research tool missing key."
        try:
            res = self.tavily.search(query=query, max_results=2)
            return f"Research: {'. '.join([r['content'][:200] for r in res['results']])}"
        except: return "Research failed."

# --- 4. ROUTING ---
def get_intent(user_input):
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"Output JSON ONLY. Tools: ADD_INV, CHECK_INV, CREATE_TICKET, LIST_TICKETS, CALENDAR, RESEARCH, CHAT. Today: {today}. Input: {user_input}"
    try:
        res = ollama.chat(model='llama3.1', messages=[{'role': 'user', 'content': prompt}])
        c = res['message']['content']
        return json.loads(c[c.find('{'):c.rfind('}')+1])
    except: return {"tool": "CHAT", "args": {"message": "Parsing error."}}

# --- 5. MAIN ---
def main():
    if not os.path.exists(SPEAKER_WAV):
        with wave.open(SPEAKER_WAV, "w") as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
            for _ in range(44100): f.writeframesraw(struct.pack('<h', 0))

    audio = AudioEngine()
    shop = ShopOS(audio)
    
    # Run Daily Briefing on Start
    briefing = shop.daily_briefing()
    print(f"{Fore.CYAN}>> {briefing}{Style.RESET_ALL}")
    audio.speak(briefing)

    while True:
        mode = input(f"\n{Fore.WHITE}[T]ype, [V]oice, [Q]uit > {Style.RESET_ALL}").lower().strip()
        if mode == 'q': break
        user_text = ""
        if mode == 'v':
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening...")
                try: user_text = r.recognize_google(r.listen(source, timeout=5))
                except: continue
        elif mode == 't': user_text = input("Command: ")

        if user_text:
            intent = get_intent(user_text)
            tool, args = intent.get("tool"), intent.get("args", {})
            if tool == "ADD_INV": response = shop.inventory_add(args.get('item'), args.get('price'), args.get('qty', 1))
            elif tool == "CHECK_INV": response = shop.inventory_check(args.get('query'))
            elif tool == "CREATE_TICKET": response = shop.create_ticket(args.get('description'))
            elif tool == "LIST_TICKETS": response = shop.list_tickets()
            elif tool == "CALENDAR": response = shop.google_calendar(args.get('summary'), args.get('time'))
            elif tool == "RESEARCH": response = shop.research(args.get('query'))
            else: response = args.get("message", "I didn't understand.")
            
            print(f"{Fore.GREEN}>> {response}{Style.RESET_ALL}")
            audio.speak(response)

if __name__ == "__main__":
    main()