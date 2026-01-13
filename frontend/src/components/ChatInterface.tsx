import { useState, useEffect, useRef } from 'react';

export default function ChatInterface() {
  const [messages, setMessages] = useState<{sender: string, text: string}[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (event: any) => {
      if (isProcessing) return;
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        transcript += event.results[i][0].transcript + ' ';
      }

      if (event.results[event.results.length - 1].isFinal) {
        const cleanText = transcript.trim().toLowerCase();
        const triggers = ['add', 'check', 'research', 'remove', 'delete', 'stock'];
        if (triggers.some(t => cleanText.includes(t))) {
          handleCommand(cleanText);
        }
      }
    };

    recognition.onend = () => { if (!isProcessing) recognition.start(); };
    recognition.start();
    recognitionRef.current = recognition;
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
    } catch { setIsProcessing(false); }
  };

  const speak = (text: string) => {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    const safetyTimer = setTimeout(() => setIsProcessing(false), 10000);
    utterance.onend = () => {
      clearTimeout(safetyTimer);
      setIsProcessing(false);
    };
    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="bg-slate-900 border-2 border-blue-500/20 rounded-3xl p-8 w-full max-w-2xl shadow-2xl">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-xl font-bold text-blue-500 uppercase tracking-tighter">Shop OS v3.5</h1>
        <div className={`h-3 w-3 rounded-full ${isProcessing ? 'bg-red-500 animate-pulse' : 'bg-green-500 shadow-[0_0_10px_green]'}`} />
      </div>
      <div className="h-96 overflow-y-auto space-y-4 mb-4 scrollbar-hide">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`p-4 rounded-2xl text-sm ${m.sender === 'user' ? 'bg-blue-600 text-white shadow-lg' : 'bg-slate-800 text-slate-300'}`}>
              {m.text}
            </div>
          </div>
        ))}
      </div>
      <p className="text-[10px] text-slate-600 font-bold uppercase text-center">{isProcessing ? "Speaking..." : "Listening"}</p>
    </div>
  );
}
