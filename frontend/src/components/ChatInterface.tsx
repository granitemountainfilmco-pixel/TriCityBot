import { useState, useEffect, useRef } from 'react';

export default function ChatInterface() {
  const [messages, setMessages] = useState<{sender: string, text: string}[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    if (!SpeechRecognition) return;

    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.continuous = true;
    
    recognitionRef.current.onresult = (event: any) => {
      if (isProcessing) return;
      const transcript = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
      
      // Keywords that trigger the system
      const triggers = ['add', 'check', 'research', 'remove', 'search', 'delete'];
      if (triggers.some(t => transcript.startsWith(t))) {
        handleCommand(transcript);
      }
    };

    recognitionRef.current.onend = () => recognitionRef.current.start();
    recognitionRef.current.start();
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

      // Robust Speech Synthesis
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(data.response);
      utterance.onend = () => setIsProcessing(false);
      window.speechSynthesis.speak(utterance);
    } catch (err) {
      setIsProcessing(false);
    }
  };

  return (
    <div className="bg-slate-900 border-2 border-blue-500/20 rounded-3xl p-8 w-full max-w-2xl shadow-2xl">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-xl font-black text-blue-500 tracking-widest uppercase">TriCity Shop v2.0</h1>
        <div className={`h-2 w-2 rounded-full ${isProcessing ? 'bg-yellow-500 animate-ping' : 'bg-green-500'}`} />
      </div>
      <div className="h-96 overflow-y-auto space-y-4 mb-4 pr-2">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`p-4 rounded-2xl text-sm ${m.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-300'}`}>
              {m.text}
            </div>
          </div>
        ))}
      </div>
      <div className="text-[10px] text-slate-600 font-bold uppercase text-center tracking-widest">
        System Listening for Add / Remove / Research
      </div>
    </div>
  );
}
