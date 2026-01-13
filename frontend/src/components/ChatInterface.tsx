import { useState } from 'react';

interface Message {
  sender: 'user' | 'bot';
  text: string;
}

export default function ChatInterface() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // --- Browser Voice Recognition ---
  const startListening = () => {
    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    
    if (!SpeechRecognition) {
      alert("Voice recognition not supported in this browser. Please use Chrome.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      handleSend(transcript);
    };

    recognition.start();
  };

  // --- Communication with Python Backend ---
  const handleSend = async (text: string) => {
    if (!text.trim()) return;

    const userMsg: Message = { sender: 'user', text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });

      const data = await response.json();
      const botMsg: Message = { sender: 'bot', text: data.response };
      
      setMessages(prev => [...prev, botMsg]);

      // Simple Text-to-Speech (Feedback)
      const speech = new SpeechSynthesisUtterance(data.response);
      window.speechSynthesis.speak(speech);

    } catch (error) {
      setMessages(prev => [...prev, { sender: 'bot', text: "Error: Backend not reachable." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden">
      {/* Message Display */}
      <div className="h-[500px] overflow-y-auto p-6 space-y-4 bg-slate-800/50">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`px-4 py-2 rounded-2xl max-w-[85%] ${
              msg.sender === 'user' 
                ? 'bg-blue-600 text-white rounded-tr-none' 
                : 'bg-slate-700 text-slate-100 rounded-tl-none border border-slate-600'
            }`}>
              <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
            </div>
          </div>
        ))}
        {isLoading && <div className="text-blue-400 text-xs animate-pulse">Assistant is thinking...</div>}
      </div>

      {/* Input Controls */}
      <div className="p-4 bg-slate-900/80 border-t border-slate-700 flex items-center gap-3">
        <button
          onClick={startListening}
          className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
            isListening ? 'bg-red-500 scale-110' : 'bg-slate-700 hover:bg-slate-600'
          }`}
        >
          {isListening ? '🛑' : '🎤'}
        </button>
        
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend(input)}
          placeholder="Ask about inventory or research..."
          className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <button
          onClick={() => handleSend(input)}
          className="bg-blue-600 hover:bg-blue-500 px-5 py-3 rounded-xl font-semibold transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  );
}
