import ChatInterface from './components/ChatInterface';

function App() {
  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-4">
      <h1 className="text-3xl font-bold text-blue-500 mb-8">SHOP OS v1.0</h1>
      <ChatInterface />
    </div>
  );
}

export default App;
