import ChatInterface from './components/ChatInterface';

function App() {
  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center p-4">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-extrabold text-blue-500 tracking-tight">
          SHOP<span className="text-slate-100">OS</span>
        </h1>
        <p className="text-slate-400 text-sm mt-2">Voice-Activated Inventory & Research</p>
      </header>
      
      <main className="w-full max-w-2xl">
        <ChatInterface />
      </main>

      <footer className="mt-8 text-slate-500 text-xs">
        Connected to Ollama Local LLM
      </footer>
    </div>
  );
}

export default App;
