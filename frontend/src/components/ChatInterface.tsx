import { useState, useEffect, useRef } from 'react';

export default function ChatInterface() {
  const [messages, setMessages] = useState<{sender: string, text: string}[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [micStatus, setMicStatus] = useState('OFF');
  const recognitionRef = useRef<any>(null);

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
    // FIXED: Correct class name
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onstart = () => { if (recognitionRef.current) recognitionRef.current.stop(); };
    utterance.onend = () => {
      setIsProcessing(false);
      if (recognitionRef.current) recognitionRef.current.start();
    };
    window.speechSynthesis.speak(utterance);
  };

  // ... (rest of your Mic initialization logic here)
  return (
    <div className="bg-slate-900 rounded-3xl p-8 w-full max-w-2xl text-white">
        {/* Your UI Components */}
    </div>
  );
}
