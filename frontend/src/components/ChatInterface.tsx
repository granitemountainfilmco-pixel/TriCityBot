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
    recognition.interimResults = true;

    recognition.onstart = () => { isStarted.current = true; setMicStatus('ON'); };
    recognition.onresult = (event: any) => {
      if (isProcessing) return;
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        transcript += event.results[i][0].transcript + ' ';
      }
      if (event.results[event.results.length - 1].isFinal) {
        const cleanText = transcript.trim().toLowerCase();
        if (cleanText.length > 2) handleCommand(cleanText);
      }
    };
    recognition.onend = () => {
      isStarted.current = false;
      setMicStatus('OFF');
      if (!isProcessing) setTimeout(() => { if (!isStarted.current) recognition.start(); }, 300);
    };
    recognitionRef.current = recognition;
    recognition.start();
  };

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
    const safety = setTimeout(() => setIsProcessing(false), 12000);
    utterance.onend = () => {
      clearTimeout(safety);
      setIsProcessing(false);
    };
    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="bg-slate-900 border-2 border-blue-500/20 rounded-3xl p-8 w-full max-w-2xl shadow-2xl text-white font-sans">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-xl font-bold text-blue-500 uppercase tracking-tighter">Shop OS v3.9</h1>
          <p className={`text-[10px] ${isProcessing ? 'text-red-500 animate-pulse' : 'text-green-500'}`}>
            {isProcessing ? 'PROCESSING...' : 'LISTENING'}
          </p>
        </div>
        <button onClick={initMic} className={`px-4 py-2 rounded-xl text-[10px] font-black ${micStatus === 'ON' ? 'bg-green-500/10 text-green-500 border border-green-500' : 'bg-blue-600 animate-bounce'}`}>
          {micStatus === 'ON' ? 'MIC LIVE' : 'ACTIVATE MIC'}
        </button>
      </div>
      <div className="h-80 overflow-y-auto space-y-4 mb-4 scrollbar-hide">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`p-4 rounded-2xl text-sm ${m.sender === 'user' ? 'bg-blue-600' : 'bg-slate-800'}`}>{m.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
