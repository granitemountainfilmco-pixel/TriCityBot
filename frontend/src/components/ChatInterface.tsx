// Partial update for the handleCommand and speak functions
const handleCommand = async (text: string) => {
  if (isProcessing) return; // Prevent overlapping commands
  
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
      setIsProcessing(false); // Reset if trigger word wasn't found
    }
  } catch (err) {
    console.error("Chat Error:", err);
    setIsProcessing(false);
  }
};

const speak = (text: string) => {
  window.speechSynthesis.cancel();
  const utterance = new SynthesisUtterance(text);
  
  utterance.onstart = () => {
    // Ensure mic is definitely off while speaking
    if (recognitionRef.current) recognitionRef.current.stop();
  };

  utterance.onend = () => {
    setIsProcessing(false);
    // Restart recognition after speaking is done
    if (recognitionRef.current) recognitionRef.current.start();
  };

  window.speechSynthesis.speak(utterance);
};
