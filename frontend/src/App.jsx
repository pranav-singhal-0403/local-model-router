
import { useState } from "react";
import ChatWindow from "./components/ChatWindow";
import DocumentLibrary from "./components/DocuemntLibrary";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("chat");
  const [pageKey, setPageKey] = useState(0);

  function navigate(tab) {
    if (tab === activeTab) return;

    setActiveTab(tab);
    setPageKey((current) => current + 1);
  }

  return (
    <div className="workspace">
      <aside className="sidebar">
        <button
          className="workspace-brand"
          onClick={() => navigate("chat")}
          aria-label="Go to chat"
        >
          <span className="brand-mark">R</span>
          <span>Local Model Router</span>
        </button>

        <div className="sidebar-label">WORKSPACE</div>

        <nav className="sidebar-nav">
          <button
            className={`nav-item ${activeTab === "chat" ? "active" : ""}`}
            onClick={() => navigate("chat")}
          >
            <span className="nav-icon">◌</span>
            Chat
          </button>

          <button
            className={`nav-item ${
              activeTab === "documents" ? "active" : ""
            }`}
            onClick={() => navigate("documents")}
          >
            <span className="nav-icon">▤</span>
            Documents
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="local-indicator">
            <span className="status-dot" />
            <div>
              <strong>Local environment</strong>
              <span>Ollama · Qdrant</span>
            </div>
          </div>

          <div className="sidebar-version">Local Model Router · v0.1.0</div>
        </div>
      </aside>

      <main className="workspace-main">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span>{" "}
            {activeTab === "chat" ? "Chat" : "Documents"}
          </div>

          <div className="model-indicator">
            <span className="status-dot" />
            gemma3:4b
          </div>
        </header>

        <div className="mobile-tabs">
          <button
            className={activeTab === "chat" ? "active" : ""}
            onClick={() => navigate("chat")}
          >
            Chat
          </button>
          <button
            className={activeTab === "documents" ? "active" : ""}
            onClick={() => navigate("documents")}
          >
            Documents
          </button>
        </div>

        <section
          key={pageKey}
          className={`page-content ${
            activeTab === "chat" ? "chat-page" : "documents-page"
          }`}
        >
          {activeTab === "chat" ? (
            <ChatWindow />
          ) : (
            <DocumentLibrary />
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
