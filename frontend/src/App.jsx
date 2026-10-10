import { useCallback, useEffect, useState } from "react";
import ChatWindow from "./components/ChatWindow";
import DocumentLibrary from "./components/DocuemntLibrary";
import {
  createConversation,
  getConversations,
  deleteConversation,
} from "./services/api";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("chat");
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [historyLoading, setHistoryLoading] = useState(true);
  const [creatingChat, setCreatingChat] = useState(false);
  const [sidebarError, setSidebarError] = useState("");
  const refreshConversations = useCallback(async () => {
    try {
      const result = await getConversations();
      setConversations(result.conversations || []);
      setSidebarError("");
    } catch {
      setSidebarError("Unable to load chat history.");
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    let ignore = false;

    async function loadInitialConversations() {
      try {
        const result = await getConversations();

        if (!ignore) {
          setConversations(result.conversations || []);
          setSidebarError("");
        }
      } catch {
        if (!ignore) {
          setSidebarError("Unable to load chat history.");
        }
      } finally {
        if (!ignore) {
          setHistoryLoading(false);
        }
      }
    }

    loadInitialConversations();

    return () => {
      ignore = true;
    };
  }, []);

  async function handleNewChat() {
    if (creatingChat) return;

    setCreatingChat(true);
    setSidebarError("");

    try {
      const conversation = await createConversation();
      setConversations((current) => [
        {
          ...conversation,
          message_count: 0,
          updated_at: new Date().toISOString(),
        },
        ...current,
      ]);
      setActiveConversationId(conversation.id);
      setActiveTab("chat");
    } catch {
      setSidebarError("Unable to create a new chat.");
    } finally {
      setCreatingChat(false);
    }
  }

  function handleConversationUpdated() {
    refreshConversations();
  }

  async function handleDeleteConversation(event, conversationId) {
    event.stopPropagation();

    if (!window.confirm("Delete this conversation and its messages?")) {
      return;
    }

    try {
      await deleteConversation(conversationId);
      setConversations((current) =>
        current.filter((conversation) => conversation.id !== conversationId)
      );

      if (activeConversationId === conversationId) {
        setActiveConversationId(null);
      }
    } catch {
      setSidebarError("Unable to delete this conversation.");
    }
  }

  function navigate(tab) {
    setActiveTab(tab);
  }

  const filteredConversations = conversations.filter((conversation) =>
    (conversation.title || "New chat")
      .toLowerCase()
      .includes(searchQuery.trim().toLowerCase())
  );

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

        <div className="chat-history">
          <div className="chat-history-heading">
            <span>YOUR CHATS</span>
            <button
              className="new-chat-button"
              onClick={handleNewChat}
              disabled={creatingChat}
              title="Start a new chat"
            >
              <span>＋</span>
              New chat
            </button>
          </div>

          <input
            className="chat-search"
            type="search"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            aria-label="Search conversations"
          />

          <div className="conversation-list">
            {historyLoading && (
              <div className="history-message">Loading conversations...</div>
            )}

            {!historyLoading && filteredConversations.length === 0 && (
              <div className="history-message">
                {searchQuery.trim()
                  ? "No matching conversations."
                  : "Your conversations will appear here."}
              </div>
            )}

            {filteredConversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`conversation-item ${
                  activeConversationId === conversation.id ? "active" : ""
                }`}
              >
                <button
                  className="conversation-select"
                  onClick={() => {
                    setActiveConversationId(conversation.id);
                    setActiveTab("chat");
                  }}
                  title={conversation.title || "New chat"}
                >
                  <span className="conversation-icon">◌</span>
                  <span className="conversation-title">
                    {conversation.title || "New chat"}
                  </span>
                </button>

                <button
                  className="conversation-delete"
                  onClick={(event) =>
                    handleDeleteConversation(event, conversation.id)
                  }
                  title="Delete conversation"
                  aria-label={`Delete ${conversation.title || "conversation"}`}
                >
                  ×
                </button>
              </div>
            ))}
          </div>

          {sidebarError && (
            <div className="history-error">{sidebarError}</div>
          )}
        </div>

        <div className="sidebar-bottom">
          <div className="local-indicator">
            <span className="status-dot" />
            <div>
              <strong>Local environment</strong>
              <span>Ollama · Qdrant · PostgreSQL</span>
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
          className={`page-content ${
            activeTab === "chat" ? "chat-page" : "documents-page"
          }`}
          style={{ display: activeTab === "chat" ? "flex" : "none" }}
        >
          <ChatWindow
            conversationId={activeConversationId}
            onConversationUpdated={handleConversationUpdated}
            onConversationCreated={(conversation) =>{
              setActiveConversationId(conversation.id);
              setConversations((current) => [
                conversation,
                ...current.filter((item) => item.id !== conversation.id)
              ]);
            }}
          />
        </section>

        {activeTab === "documents" && (
          <section className="page-content documents-page">
            <DocumentLibrary />
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
