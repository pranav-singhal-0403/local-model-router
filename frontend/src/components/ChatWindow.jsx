import { useEffect, useRef, useState } from "react";
import {
  sendChatMessage,
  createConversation,
  getConversationMessages,
} from "../services/api";
import Message from "./Message";
import SourceCard from "./SourceCard";

function ChatWindow({
  conversationId,
  onConversationUpdated,
  onConversationCreated,
}) {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState("");
  const requestId = useRef(0);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const currentRequest = ++requestId.current;

    async function loadMessages() {
      setMessages([]);
      setError("");

      if (!conversationId) {
        setHistoryLoading(false);
        return;
      }

      setHistoryLoading(true);

      try {
        const result = await getConversationMessages(conversationId);

        if (requestId.current === currentRequest) {
          setMessages(result.messages || []);
        }
      } catch {
        if (requestId.current === currentRequest) {
          setError("Unable to load this conversation's messages.");
        }
      } finally {
        if (requestId.current === currentRequest) {
          setHistoryLoading(false);
        }
      }
    }

    loadMessages();

    return () => {
      requestId.current += 1;
    };
  }, [conversationId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSubmit(event) {
    event.preventDefault();

    const trimmedQuery = query.trim();

    if (!trimmedQuery || loading) return;

    setQuery("");
    setLoading(true);
    setError("");

    let currentConversationId = conversationId;

    setMessages((current) => [
      ...current,
      { role: "user", content: trimmedQuery },
    ]);

    try {
      if (!currentConversationId) {
        const conversation = await createConversation();
        currentConversationId = conversation.id;
        onConversationCreated?.(conversation);
      }

      const result = await sendChatMessage(
        trimmedQuery,
        5,
        currentConversationId
      );

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: result.answer,
          sources: result.sources || [],
          latency: result.latency || null,
        },
      ]);

      onConversationUpdated?.();
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          requestError.message ||
          "Something went wrong while processing your query."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-window">
      <div className="messages">
        {historyLoading && (
          <div className="loading">Loading conversation...</div>
        )}

        {!historyLoading && messages.length === 0 && (
          <div className="empty-state">
            <span>What would you like to explore?</span>
            <span>Ask a question about your indexed documents.</span>
          </div>
        )}

        {messages.map((message, index) => (
          <div className="message-container" key={message.id || index}>
            <Message role={message.role} content={message.content} />

            {message.role === "assistant" && message.sources?.length > 0 && (
              <div className="sources">
                <div className="sources-title">
                  Sources from your documents
                </div>

                {message.sources.map((source, sourceIndex) => (
                  <SourceCard
                    key={source.chunk_id || sourceIndex}
                    source={source}
                  />
                ))}
              </div>
            )}

            {message.role === "assistant" && message.latency && (
              <div className="latency">
                Retrieval {message.latency.retrieval_ms} ms
                {" · "}
                Generation {message.latency.generation_ms} ms
                {" · "}
                Total {message.latency.total_ms} ms
              </div>
            )}
          </div>
        ))}

        {loading && <div className="loading">Preparing your answer…</div>}

        {error && <div className="chat-error">{error}</div>}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input" onSubmit={handleSubmit}>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Message your document assistant..."
          disabled={loading || historyLoading}
          aria-label="Message your document assistant"
        />

        <button
          type="submit"
          disabled={loading || historyLoading || !query.trim()}
        >
          {loading ? "Working…" : "Send"}
        </button>
      </form>
    </div>
  );
}

export default ChatWindow;