import { useState, useEffect, useRef } from 'react';

export default function ChatInterface() {
  const [messages, setMessages] = useState<{sender: string, text: string}[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const recognitionRef = useRef<any>(null);

useEffect(() => {
    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    if (!SpeechRecognition) return;

    recognitionRef.current = new SpeechRecognition();
    
    // 1. IMPROVED SETTINGS FOR ACCURACY
    recognitionRef.current.continuous = true;
    recognitionRef.current.interimResults = true; // Allows the AI to "correct" misheard words
    recognitionRef.current.lang = 'en-US';
    recognitionRef.current.maxAlternatives = 1;

    let finalTranscript = '';

    recognitionRef.current.onresult = (event: any) => {
      if (isProcessing) return;

      let interimTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript = event.results[i][0].transcript.trim().toLowerCase();
          
          // 2. TRIGGER VALIDATION
          // We check the final "corrected" version for our shop keywords
          const triggers = ['add', 'check', 'research', 'remove', 'search', 'delete', 'stock'];
          if (triggers.some(t => finalTranscript.includes(t))) {
            handleCommand(finalTranscript);
            finalTranscript = ''; // Reset after trigger
          }
        } else {
          interimTranscript += event.results[i][0].transcript;
          // You could optionally show this "live" text in the UI
        }
      }
    };

    recognitionRef.current.onend = () => {
      // Auto-restart if not processing to keep the "Always Listening" feel
      if (!isProcessing) recognitionRef.current.start();
    };

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

      // --- VOICE OUTPUT ---
      window.speechSynthesis.cancel(); // Clear queue
      const utterance = new SpeechSynthesisUtterance(data.response);
      utterance.onend = () => setIsProcessing(false); // Resume listening after speaking
      window.speechSynthesis.speak(utterance);
    } catch (err) {
      setIsProcessing(false);
    }
  };

  return (
    <div className="bg-slate-900 border-2 border-blue-500/20 rounded-3xl p-8 w-full max-w-2xl shadow-2xl font-sans">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-xl font-bold text-blue-500 tracking-widest">TRI-CITY ASSISTANT</h1>
        <div className={`h-3 w-3 rounded-full ${isProcessing ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'}`} />
      </div>
      <div className="h-96 overflow-y-auto space-y-4 mb-6 pr-2">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`p-4 rounded-2xl text-sm ${m.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-300'}`}>
              {m.text}
            </div>
          </div>
        ))}
      </div>
      <p className="text-[10px] text-slate-500 text-center uppercase tracking-widest">
        Voice Commands: Add | Remove | Check | Research
      </p>
    </div>
  );
}
