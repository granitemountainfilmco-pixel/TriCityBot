import { useState, useEffect, useRef } from 'react';

interface Message {
  sender: 'user' | 'bot';
  text: string;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const recognitionRef = useRef<any>(null);

  // Initialize Speech Recognition once
  useEffect(() => {
    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onstart = () => setIsListening(true);
      recognitionRef.current.onend = () => setIsListening(false);
      
      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        handleSend(transcript);
      };
    }
  }, []);

  const startListening = () => {
    try {
      recognitionRef.current?.start();
    } catch (e) {
      console.log("Recognition already started or blocked.");
    }
  };

  const handleSend = async (text: string) => {
    if (!text.trim()) return;
    setMessages(prev => [...prev, { sender: 'user', text }]);
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { sender: 'bot', text: data.response }]);

      // --- AUTO-VOICE ACTIVATION LOOP ---
      const utterance = new SpeechSynthesisUtterance(data.response);
      utterance.onend = () => {
        console.log("AI finished. Restarting listener...");
        startListening(); // This makes it voice-activated
      };
      window.speechSynthesis.speak(utterance);

    } catch (err) {
      setMessages(prev => [...prev, { sender: 'bot', text: "Server error." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-xl shadow-2xl p-6 w-full max-w-2xl border border-slate-700">
      <div className="h-96 overflow-y-auto mb-4 space-y-4 pr-2">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`p-3 rounded-lg text-sm ${m.sender === 'user' ? 'bg-blue-600' : 'bg-slate-700 text-slate-200'}`}>
              {m.text}
            </div>
          </div>
        ))}
        {isLoading && <div className="text-xs text-blue-400 animate-pulse">Assistant is thinking...</div>}
      </div>
      <div className="flex gap-2">
        <button 
          onClick={startListening}
          className={`p-4 rounded-full ${isListening ? 'bg-red-500 animate-pulse' : 'bg-slate-600'}`}
        >
          🎤
        </button>
        <input 
          className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 text-white"
          placeholder="Speak or type..."
          onKeyDown={(e) => e.key === 'Enter' && handleSend((e.target as HTMLInputElement).value)}
        />
      </div>
    </div>
  );
}
