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
    recognition.interimResults = true; // High accuracy mode
    recognition.lang = 'en-US';

    recognition.onresult = (event: any) => {
      // If we are currently "processing" (AI is thinking or talking), ignore input
      if (isProcessing) return;

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          const transcript = event.results[i][0].transcript.trim().toLowerCase();
          console.log("Finalized Speech:", transcript);

          // Trigger keywords
          const triggers = ['add', 'check', 'research', 'remove', 'search', 'delete', 'stock', 'do we'];
          if (triggers.some(t => transcript.includes(t))) {
            handleCommand(transcript);
          }
        }
      }
    };

    // Keep the mic alive
    recognition.onend = () => {
      if (!isProcessing) recognition.start();
    };

    recognition.start();
    recognitionRef.current = recognition;

    return () => recognition.stop();
  }, [isProcessing]);

  const handleCommand = async (text: string) => {
    setIsProcessing(true); // Locks the mic
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
      console.error("Fetch error:", err);
      setIsProcessing(false); // Unlock mic on error
    }
  };

  const speak = (text: string) => {
    window.speechSynthesis.cancel(); // Kill any stuck audio
    
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Safety Force-Unlock: If speech hangs, unlock the mic after 8 seconds anyway
    const forceUnlock = setTimeout(() => {
      console.log("Force unlocking mic...");
      setIsProcessing(false);
    }, 8000);

    utterance.onend = () => {
      clearTimeout(forceUnlock);
      setIsProcessing(false); // RE-ENABLES THE MIC
      console.log("Speech finished, mic open.");
    };

    // Ensure a natural voice is selected
    const voices = window.speechSynthesis.getVoices();
    utterance.voice = voices.find(v => v.lang === 'en-US') || voices[0];
    utterance.rate = 1.0;

    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="bg-slate-900 border-2 border-blue-500/20 rounded-3xl p-8 w-full max-w-2xl shadow-2xl">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-xl font-bold text-blue-500 tracking-widest">SHOP OS v3.0</h1>
        <div className={`h-3 w-3 rounded-full ${isProcessing ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`} />
      </div>
      <div className="h-96 overflow-y-auto space-y-4 mb-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`p-4 rounded-2xl text-sm ${m.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-300'}`}>
              {m.text}
            </div>
          </div>
        ))}
      </div>
      <div className="text-[10px] text-slate-500 text-center uppercase">
        {isProcessing ? "AI is Speaking / Thinking" : "Mic Active: Speak a Command"}
      </div>
    </div>
  );
}
