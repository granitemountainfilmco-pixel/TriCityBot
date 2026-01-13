import { useState, useEffect, useRef } from 'react';

export default function ChatInterface() {
  const [messages, setMessages] = useState<{sender: string, text: string}[]>([]);
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  // KEYWORDS: Define what triggers the AI
  const KEYWORDS = {
    ADD: ['add', 'ad', 'added', 'at'],
    RESEARCH: ['research', 'search', 'find'],
    CHECK: ['check', 'status', 'inventory']
  };

  useEffect(() => {
    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true; // Stay on
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
        console.log("Heard:", transcript);

        // Check if the transcript starts with a keyword
        const words = transcript.split(' ');
        const firstWord = words[0];

        const isTriggered = 
          KEYWORDS.ADD.includes(firstWord) || 
          KEYWORDS.RESEARCH.includes(firstWord) || 
          KEYWORDS.CHECK.includes(firstWord);

        if (isTriggered) {
          handleSend(transcript);
        } else {
          console.log("Ignored: No keyword detected.");
        }
      };

      recognitionRef.current.onend = () => {
        // Auto-restart if it drops, unless we manually stopped it
        recognitionRef.current.start();
      };

      recognitionRef.current.start();
    }
  }, []);

  const handleSend = async (text: string) => {
    setMessages(prev => [...prev, { sender: 'user', text }]);

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { sender: 'bot', text: data.response }]);

      // Speak back the result
      const utterance = new SpeechSynthesisUtterance(data.response);
      window.speechSynthesis.speak(utterance);
    } catch (err) {
      console.error("Server error");
    }
  };

  return (
    <div className="bg-slate-800 rounded-xl p-6 w-full max-w-2xl border border-slate-700">
      <div className="text-xs text-slate-400 mb-4 uppercase tracking-widest">
        Active Keywords: {Object.values(KEYWORDS).flat().join(', ')}
      </div>
      <div className="h-80 overflow-y-auto mb-4 space-y-2">
        {messages.map((m, i) => (
          <div key={i} className={`text-sm ${m.sender === 'user' ? 'text-blue-400' : 'text-slate-200'}`}>
            <b>{m.sender.toUpperCase()}:</b> {m.text}
          </div>
        ))}
      </div>
      <div className="flex items-center gap-2 text-green-500 text-xs animate-pulse">
        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
        Listening for commands...
      </div>
    </div>
  );
}
