import ChatInterface from "./components/ChatInterface";

function App() {
  return (
    /* The slate-950 and flex classes ensure the interface 
       is centered and looks consistent with the Shop OS theme.
    */
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <ChatInterface />
    </div>
  );
}

export default App;
