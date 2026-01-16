# Shop OS

All-in-one local AI assistant for Tri City Computers. Unified Python script for voice control, inventory management, and shop scheduling.

## Commands

Say "Shop" or "Hey Shop" followed by a command:

* Add Item: "Shop add RTX 4090 for 1600 dollars"
* Check Stock: "Shop check inventory for thermal paste"
* Remove Item: "Shop remove power supply"
* Tickets: "Shop create ticket to repair front desk PC"
* Reminders: "Shop remind me to order parts at 3pm"
* Calendar: "Shop add event for client meeting Friday at 1pm"

## Requirements

* Python 3.13
* Ollama with Llama 3.1 model
* Google Calendar API credentials
* Microphone and Speaker

## Setup

1. Install Ollama and run: ollama pull llama3.1
2. Place credentials.json (Google API) in the root folder
3. Place speaker.wav (Arnold voice sample) in the root folder
4. Install dependencies: pip install -r requirements.txt
5. Run the assistant: python shop_os.py

## Operation Modes

* [V]oice: Continuous listening for wake word
* [T]ype: Manual command entry
* [Q]uit: Exit application

This video provides the essential technical foundation for the Google Calendar integration used in this script, showing how to handle authentication and event management in a Python environment.
