import { useState, useEffect, useRef } from 'react';

export default function ChatInterface() {
  const [messages, setMessages] = useState<{sender: string, text: string}[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [micActive, setMicActive] = useState(false);
  const recognitionRef = useRef<any>(null);

  // Function to initialize and start the Mic
  const startMic = () => {
    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    if (!SpeechRecognition) {
      console.error("Speech recognition not supported in this browser.");
      return;
    }

    if (!recognitionRef.current) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onstart = () => {
        setMicActive(true);
        console.log("Mic is now listening...");
      };

      recognitionRef.current.onresult = (event: any) => {
        if (isProcessing) return;

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            const transcript = event.results[i][0].transcript.trim().toLowerCase();
            console.log("Captured:", transcript);

            // Trigger list
            const triggers = ['add', 'check', 'research', 'remove', 'delete', 'stock'];
            if (triggers.some(t => transcript.includes(t))) {
              handleCommand(transcript);
            }
          }
        }
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error("Speech Recognition Error:", event.error);
        if (event.error === 'not-allowed') alert("Please allow microphone access in your browser settings.");
        setMicActive(false);
      };

      recognitionRef.current.onend = () => {
        setMicActive(false);
        // Auto-restart if we aren't currently talking to the AI
        if (!isProcessing) {
            setTimeout(() => recognitionRef.current.start(), 200);
        }
      };
    }

    try {
      recognitionRef.current.start();
    } catch (e) {
      console.log("Mic already active or restarting.");
    }
  };

  useEffect(() => {
    startMic(); // Initial attempt
  }, [isProcessing]);

  const handleCommand = async (text: string) => {
    setIsProcessing(true);
    setMessages(prev => [...prev, { sender: 'user', text }]);

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { sender: 'bot', text: data.response }]);
      speak(data.response);
    } catch (err) {
      console.error("Backend unreachable:", err);
      setIsProcessing(false);
    }
  };

  const speak = (text: string) => {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Safety Force-Unlock
    const timer = setTimeout(() => setIsProcessing(false), 10000);

    utterance.onend = () => {
      clearTimeout(timer);
      setIsProcessing(false);
    };

    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="bg-slate-900 border-2 border-blue-500/20 rounded-3xl p-8 w-full max-w-2xl shadow-2xl">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-xl font-bold text-blue-500 tracking-widest uppercase">TriCity Bot</h1>
        <button 
          onClick={startMic}
          className={`px-3 py-1 rounded-full text-[10px] font-bold transition-all ${micActive ? 'bg-green-500/20 text-green-500' : 'bg-red-500 text-white animate-pulse'}`}
        >
          {micActive ? 'MIC ACTIVE' : 'RESTART MIC'}
        </button>
      </div>
      
      <div className="h-96 overflow-y-auto space-y-4 mb-4 scrollbar-hide">
        {messages.length === 0 && (
            <div className="text-slate-600 text-center italic mt-20">Waiting for command...</div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`p-4 rounded-2xl text-sm ${m.sender === 'user' ? 'bg-blue-600 text-white shadow-lg' : 'bg-slate-800 text-slate-300'}`}>
              {m.text}
            </div>
          </div>
        ))}
      </div>
      <div className="text-[10px] text-slate-500 text-center uppercase tracking-tighter">
        Try saying: "Add GPU for 500" or "Research Ryzen 9"
      </div>
    </div>
  );
}
