import { useState, useEffect, useRef } from 'react';

export default function ChatInterface() {
  const [messages, setMessages] = useState<{sender: string, text: string}[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [micStatus, setMicStatus] = useState('OFF');
  const recognitionRef = useRef<any>(null);

  const startListening = () => {
    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    if (!SpeechRecognition) return alert("Browser not supported");

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setMicStatus('ON');
    recognition.onresult = (event: any) => {
      const transcript = event.results[event.results.length - 1][0].transcript;
      const text = transcript.trim().toLowerCase();
      
      // ONLY trigger if it hears "shop" or "hey shop"
      if (text.includes("shop") || text.includes("assistant")) {
        handleCommand(text);
      }
    };

    recognition.onend = () => {
      // Auto-restart loop unless we are currently speaking
      if (!isProcessing) {
        try { recognition.start(); } catch(e) {}
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const handleCommand = async (text: string) => {
    if (isProcessing) return;
    setIsProcessing(true);
    setMessages(prev => [...prev, { sender: 'user', text }]);

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      if (data.response) {
        setMessages(prev => [...prev, { sender: 'bot', text: data.response }]);
        speak(data.response);
      } else {
        setIsProcessing(false);
      }
    } catch (err) {
      setIsProcessing(false);
    }
  };

  const speak = (text: string) => {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    
    utterance.onstart = () => {
        if (recognitionRef.current) recognitionRef.current.stop();
    };

    utterance.onend = () => {
      setIsProcessing(false);
      // Restart mic after talking
      try { recognitionRef.current.start(); } catch(e) {}
    };

    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="bg-slate-900 border-2 border-blue-500/20 rounded-3xl p-8 w-full max-w-2xl shadow-2xl text-white font-sans">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-black text-blue-500 tracking-tighter italic">SHOP OS</h1>
        <button 
          onClick={startListening}
          className={`px-6 py-2 rounded-full font-bold transition-all ${micStatus === 'ON' ? 'bg-green-500/20 text-green-500 border border-green-500' : 'bg-blue-600 hover:bg-blue-500 animate-bounce'}`}
        >
          {micStatus === 'ON' ? 'SYSTEM ONLINE' : 'ACTIVATE MIC'}
        </button>
      </div>

      <div className="h-96 overflow-y-auto space-y-4 mb-6 pr-2">
        {messages.length === 0 && (
          <p className="text-center text-slate-500 mt-20 text-sm">Say "Hey Shop, add RTX 5090 2500" to begin.</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-4 rounded-2xl text-sm ${m.sender === 'user' ? 'bg-blue-600' : 'bg-slate-800 border border-slate-700'}`}>
              {m.text}
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-center gap-2">
        <div className={`h-2 w-2 rounded-full ${isProcessing ? 'bg-red-500 animate-ping' : 'bg-green-500'}`}></div>
        <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">
          {isProcessing ? 'Processing Response...' : micStatus === 'ON' ? 'Listening for Trigger' : 'Mic Offline'}
        </p>
      </div>
    </div>
  );
}
