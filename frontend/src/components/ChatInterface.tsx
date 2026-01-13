import { useState, useEffect, useRef } from 'react';

export default function ChatInterface() {
  const [messages, setMessages] = useState<{sender: string, text: string}[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [micStatus, setMicStatus] = useState('OFF');
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    initMic();
  }, []);

  const initMic = () => {
    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setMicStatus('ON');
    recognition.onresult = (event: any) => {
      const transcript = event.results[event.results.length - 1][0].transcript;
      handleCommand(transcript.trim());
    };
    recognition.onend = () => {
      if (!isProcessing) recognition.start();
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const handleCommand = async (text: string) => {
    if (isProcessing) return;
    
    // UI Feedback: Only show the message if it has a trigger word
    const triggers = ["hey shop", "assistant", "okay shop", "shop"];
    if (!triggers.some(t => text.toLowerCase().startsWith(t))) return;

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
    utterance.onstart = () => recognitionRef.current?.stop();
    utterance.onend = () => {
      setIsProcessing(false);
      try { recognitionRef.current?.start(); } catch(e) {}
    };
    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="bg-slate-900 border-2 border-blue-500/20 rounded-3xl p-8 w-full max-w-2xl shadow-2xl text-white">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-black text-blue-500 italic">SHOP OS</h1>
        <div className={`h-3 w-3 rounded-full ${isProcessing ? 'bg-red-500 animate-ping' : 'bg-green-500'}`}></div>
      </div>
      <div className="h-96 overflow-y-auto space-y-4 mb-4 pr-2">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`p-3 rounded-2xl text-sm ${m.sender === 'user' ? 'bg-blue-600' : 'bg-slate-800'}`}>
              {m.text}
            </div>
          </div>
        ))}
      </div>
      <p className="text-[10px] text-slate-500 text-center uppercase tracking-widest">
        {micStatus === 'ON' ? 'Listening for "Hey Shop"' : 'Mic Offline'}
      </p>
    </div>
  );
}
