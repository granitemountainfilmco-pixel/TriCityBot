import { useState, useEffect, useRef } from 'react';

export default function ChatInterface() {
  const [messages, setMessages] = useState<{sender: string, text: string}[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [micStatus, setMicStatus] = useState('OFF');
  const [inputMode, setInputMode] = useState<'VOICE' | 'TEXT'>('VOICE');
  const [inputText, setInputText] = useState('');
  const recognitionRef = useRef<any>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

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
      const text = transcript.trim();
      
      // Still enforce wake-word logic for voice
      if (text.toLowerCase().includes("shop") || text.toLowerCase().includes("assistant")) {
        handleCommand(text);
      }
    };

    recognition.onend = () => {
      // Only restart if we are in VOICE mode and not currently processing
      if (inputMode === 'VOICE' && !isProcessing) {
        try { recognition.start(); } catch(e) {}
      } else {
        setMicStatus('OFF');
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const handleCommand = async (text: string) => {
    if (!text.trim() || isProcessing) return;
    
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
      console.error(err);
      setIsProcessing(false);
    }
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleCommand(inputText);
    setInputText('');
  };

  const speak = (text: string) => {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    
    utterance.onstart = () => {
        if (recognitionRef.current) recognitionRef.current.stop();
    };

    utterance.onend = () => {
      setIsProcessing(false);
      // Restart mic only if we are still in VOICE mode
      if (inputMode === 'VOICE') {
        try { recognitionRef.current.start(); } catch(e) {}
      }
    };

    window.speechSynthesis.speak(utterance);
  };

  const toggleMode = () => {
    if (inputMode === 'VOICE') {
      if (recognitionRef.current) recognitionRef.current.stop();
      setInputMode('TEXT');
      setMicStatus('OFF');
    } else {
      setInputMode('VOICE');
      startListening();
    }
  };

  return (
    <div className="bg-slate-900 border-2 border-blue-500/20 rounded-3xl p-8 w-full max-w-2xl shadow-2xl text-white font-sans">
      <div className="flex justify-between items-center mb-8">
        <div>
            <h1 className="text-2xl font-black text-blue-500 tracking-tighter italic">SHOP OS</h1>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">v2.0 Management Suite</p>
        </div>
        
        <div className="flex gap-3">
            <button 
                onClick={toggleMode}
                className="px-4 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs font-bold hover:bg-slate-700 transition-colors"
            >
                {inputMode === 'VOICE' ? '⌨️ SWITCH TO TEXT' : '🎤 SWITCH TO VOICE'}
            </button>
            {inputMode === 'VOICE' && (
                <button 
                onClick={startListening}
                className={`px-6 py-2 rounded-xl font-bold transition-all ${micStatus === 'ON' ? 'bg-green-500/20 text-green-500 border border-green-500' : 'bg-blue-600 hover:bg-blue-500'}`}
                >
                {micStatus === 'ON' ? 'SYSTEM ONLINE' : 'ACTIVATE MIC'}
                </button>
            )}
        </div>
      </div>

      <div ref={scrollRef} className="h-96 overflow-y-auto space-y-4 mb-6 pr-2 scroll-smooth">
        {messages.length === 0 && (
          <div className="text-center mt-20">
            <p className="text-slate-500 text-sm">System ready for input.</p>
            <p className="text-slate-600 text-[10px] mt-2 italic">Try: "Hey shop, create a ticket for the oily floor"</p>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-4 rounded-2xl text-sm ${m.sender === 'user' ? 'bg-blue-600' : 'bg-slate-800 border border-slate-700'}`}>
              {m.text}
            </div>
          </div>
        ))}
      </div>

      {inputMode === 'TEXT' ? (
        <form onSubmit={handleManualSubmit} className="flex gap-2">
            <input 
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Type command (e.g. Shop add item...)"
                className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-500"
                autoFocus
            />
            <button type="submit" className="bg-blue-600 px-6 py-3 rounded-xl font-bold hover:bg-blue-500">SEND</button>
        </form>
      ) : (
        <div className="flex items-center justify-center gap-2">
            <div className={`h-2 w-2 rounded-full ${isProcessing ? 'bg-red-500 animate-ping' : 'bg-green-500'}`}></div>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">
            {isProcessing ? 'Processing Response...' : micStatus === 'ON' ? 'Listening for Trigger' : 'Mic Offline'}
            </p>
        </div>
      )}
    </div>
  );
}
