import { useState } from "react";

import { sendChatMessage } from "../services/api";

import Message from "./message";
import SourceCard from "./SourceCard";


function ChatWindow() {

  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);


  async function handleSubmit(event) {

    event.preventDefault();

    const trimmedQuery = query.trim();

    if (!trimmedQuery || loading) {
      return;
    }

    setMessages((current) => [
      ...current,
      {
        role: "user",
        content: trimmedQuery,
      },
    ]);

    setQuery("");
    setLoading(true);


    try {

      const result = await sendChatMessage(
        trimmedQuery
      );

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: result.answer,
          sources: result.sources,
          latency: result.latency,
        },
      ]);

    } catch (error) {

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            error.response?.data?.detail ||
            "Something went wrong while processing the query.",
        },
      ]);

    } finally {

      setLoading(false);

    }
  }


  return (
    <div className="chat-window">

      <div className="messages">

        {messages.length === 0 && (
          <div className="empty-state">
            Ask a question about your uploaded documents.
          </div>
        )}


        {messages.map((message, index) => (

          <div
            key={index}
            className="message-container"
          >

            <Message
              role={message.role}
              content={message.content}
            />


            {message.role === "assistant" &&
              message.sources?.length > 0 && (

              <div className="sources">

                <div className="sources-title">
                  Sources
                </div>

                {message.sources.map((source) => (
                  <SourceCard
                    key={source.chunk_id}
                    source={source}
                  />
                ))}

              </div>

            )}


            {message.latency && (
              <div className="latency">

                Retrieval:{" "}
                {message.latency.retrieval_ms} ms

                {" · "}

                Generation:{" "}
                {message.latency.generation_ms} ms

                {" · "}

                Total:{" "}
                {message.latency.total_ms} ms

              </div>
            )}

          </div>

        ))}


        {loading && (
          <div className="loading">
            Generating answer...
          </div>
        )}

      </div>


      <form
        className="chat-input"
        onSubmit={handleSubmit}
      >

        <input
          value={query}
          onChange={(event) =>
            setQuery(event.target.value)
          }
          placeholder="Ask something about your documents..."
          disabled={loading}
        />

        <button
          type="submit"
          disabled={
            loading ||
            !query.trim()
          }
        >
          Send
        </button>

      </form>

    </div>
  );
}


export default ChatWindow;