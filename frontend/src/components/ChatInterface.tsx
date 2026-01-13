import { useState, useEffect, useRef } from 'react';

export default function ChatInterface() {
  const [messages, setMessages] = useState<{sender: string, text: string}[]>([]);
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  // Synonyms to catch misheard keywords
  const KEYWORDS = {
    ADD: ['add', 'ad', 'at', 'added'],
    RESEARCH: ['research', 'search', 'find', 'google'],
    CHECK: ['check', 'status', 'inventory', 'do we have']
  };

  useEffect(() => {
    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
        console.log("Heard:", transcript);

        const firstWord = transcript.split(' ')[0];
        const isCommand = Object.values(KEYWORDS).flat().includes(firstWord);

        if (isCommand) {
          handleSend(transcript);
        }
      };

      recognitionRef.current.onend = () => recognitionRef.current.start();
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

      // Speech Synthesis
      window.speechSynthesis.cancel(); 
      const utterance = new SpeechSynthesisUtterance(data.response);
      window.speechSynthesis.speak(utterance);
    } catch (err) {
      console.error("Communication error");
    }
  };

  return (
    <div className="bg-slate-800 rounded-xl p-6 w-full max-w-2xl border border-slate-700 shadow-2xl">
      <div className="text-[10px] text-blue-400 mb-4 uppercase font-bold">
        Listening for: ADD | RESEARCH | CHECK
      </div>
      <div className="h-96 overflow-y-auto mb-4 space-y-3">
        {messages.map((m, i) => (
          <div key={i} className={`text-sm ${m.sender === 'user' ? 'text-blue-300' : 'text-slate-100'}`}>
            <span className="opacity-50">[{m.sender.toUpperCase()}]</span> {m.text}
          </div>
        ))}
      </div>
      <div className="flex items-center gap-2 text-green-500 text-xs italic">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
        </span>
        System Active
      </div>
    </div>
  );
}
