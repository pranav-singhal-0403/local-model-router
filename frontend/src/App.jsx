import ChatWindow from "./components/ChatWindow";
import UploadPanel from "./components/UploadPanel";
import "./App.css";

function App() {
  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <div className="brand-icon">R</div>
          <div>
            <h1>Local Model Router</h1>
            <p>Private, document-grounded AI</p>
          </div>
        </div>

        <div className="status">
          <span className="status-dot" />
          Local AI
        </div>
      </header>

      <main className="main">
        <section className="welcome">
          <h2>Your documents. Your AI.</h2>
          <p>
            Upload a PDF and ask questions. Answers are generated
            locally using Ollama and grounded in your documents.
          </p>
        </section>

        <section className="upload-section">
          <h3>Knowledge base</h3>
          <UploadPanel />
        </section>

        <section className="chat-section">
          <div className="section-heading">
            <div>
              <h3>Document assistant</h3>
              <p>Ask questions about indexed documents</p>
            </div>
            <span className="model-badge">gemma3:4b</span>
          </div>

          <ChatWindow />
        </section>
      </main>

      <footer className="footer">
        Local Model Router · Powered by FastAPI, Qdrant and Ollama
      </footer>
    </div>
  );
}

export default App;