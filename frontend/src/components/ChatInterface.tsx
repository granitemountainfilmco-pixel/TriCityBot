import { useState, useEffect, useRef } from 'react';

export default function ChatInterface() {
  const [messages, setMessages] = useState<{sender: string, text: string}[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [micStatus, setMicStatus] = useState('OFF');
  const recognitionRef = useRef<any>(null);
  const isStarted = useRef(false);

  const initMic = () => {
    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    if (!SpeechRecognition || isStarted.current) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => { 
      isStarted.current = true; 
      setMicStatus('ON'); 
    };

    recognition.onresult = (event: any) => {
      if (isProcessing) return;
      const transcript = event.results[event.results.length - 1][0].transcript;
      const cleanText = transcript.trim().toLowerCase();
      if (cleanText.length > 2) handleCommand(cleanText);
    };

    recognition.onend = () => {
      isStarted.current = false;
      setMicStatus('OFF');
      // Auto-restart if we aren't currently waiting for a server response
      if (!isProcessing) {
        setTimeout(() => {
          try { recognition.start(); } catch(e) {}
        }, 300);
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
      console.error("Chat Error:", err);
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
      if (recognitionRef.current && !isStarted.current) {
        try { recognitionRef.current.start(); } catch(e) {}
      }
    };

    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="bg-slate-900 border-2 border-blue-500/20 rounded-3xl p-8 w-full max-w-2xl shadow-2xl text-white font-sans">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-xl font-bold text-blue-500 uppercase tracking-tighter">Shop OS</h1>
          <p className={`text-[10px] ${isProcessing ? 'text-red-500 animate-pulse' : 'text-green-500'}`}>
            {isProcessing ? 'PROCESSING...' : 'LISTENING'}
          </p>
        </div>
        <button 
          onClick={initMic} 
          className={`px-4 py-2 rounded-xl text-[10px] font-black ${micStatus === 'ON' ? 'bg-green-500/10 text-green-500 border border-green-500' : 'bg-blue-600 animate-bounce'}`}
        >
          {micStatus === 'ON' ? 'MIC LIVE' : 'ACTIVATE MIC'}
        </button>
      </div>
      
      <div className="h-80 overflow-y-auto space-y-4 mb-6 pr-2 custom-scrollbar">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-2xl text-sm ${m.sender === 'user' ? 'bg-blue-600' : 'bg-slate-800 border border-slate-700'}`}>
              {m.text}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
