
import { useCallback, useEffect, useRef, useState } from "react";
import {
  deleteDocument,
  getDocuments,
  uploadDocument,
} from "../services/api";

function DocumentLibrary() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [deletingId, setDeletingId] = useState(null);
  const [search, setSearch] = useState("");
  const inputRef = useRef(null);

  const loadDocuments = useCallback(async () => {
    try {
        const result = await getDocuments();

        setDocuments(result.documents || []);
        setError("");
    } catch (err) {
        setError(
        err.response?.data?.detail ||
            "Could not load documents. Check that the backend is running."
        );
    } finally {
        setLoading(false);
    }
  }, []);

  useEffect(() => {
  let ignore = false;

  async function fetchInitial() {
    try {
      const result = await getDocuments();
      if (!ignore) setDocuments(result.documents || []);
    } catch (err) {
      if (!ignore) {
        setError(
          err.response?.data?.detail ||
            "Could not load documents. Check that the backend is running."
        );
      }
    } finally {
      if (!ignore) setLoading(false);
    }
  }

  fetchInitial();

  return () => {
    ignore = true;
  };
}, []);

  async function handleFiles(files) {
    const file = files?.[0];

    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are supported.");
      return;
    }

    setUploading(true);
    setError("");
    setNotice("");

    try {
      const result = await uploadDocument(file);

      setNotice(
        `${result.filename} was uploaded and indexed successfully.`
      );

      await loadDocuments();
    } catch (err) {
      setError(
        err.response?.data?.detail || "PDF upload failed."
      );
    } finally {
      setUploading(false);

      if (inputRef.current) {
        inputRef.current.value = "";
      }
    }
  }

  async function handleDelete(document) {
    const confirmed = window.confirm(
      `Delete "${document.document_name}" and all its indexed chunks? This cannot be undone.`
    );

    if (!confirmed) return;

    setDeletingId(document.document_id);
    setError("");
    setNotice("");

    try {
      await deleteDocument(document.document_id);

      setDocuments((current) =>
        current.filter(
          (item) => item.document_id !== document.document_id
        )
      );

      setNotice(`${document.document_name} was deleted.`);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Document deletion failed."
      );
    } finally {
      setDeletingId(null);
    }
  }

  const filteredDocuments = documents.filter((document) =>
    document.document_name
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  return (
    <div className="document-library">
      <div className="library-heading">
        <div>
          <div className="eyebrow">YOUR KNOWLEDGE BASE</div>
          <h2>Documents</h2>
          <p>Upload and manage the documents your AI can reference.</p>
        </div>

        <button
          className="secondary-button"
          onClick={loadDocuments}
          disabled={loading}
        >
          Refresh
        </button>
      </div>

      <label
        className={`dropzone ${dragging ? "dragging" : ""} ${
          uploading ? "uploading" : ""
        }`}
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragging(false);
          handleFiles(event.dataTransfer.files);
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          hidden
          disabled={uploading}
          onChange={(event) =>
            handleFiles(event.target.files)
          }
        />

        <span className="upload-icon">↑</span>

        <strong>
          {uploading ? "Indexing your document…" : "Add PDF documents"}
        </strong>

        <span>
          {uploading
            ? "Extracting text and creating embeddings. Please wait."
            : "Drop a PDF here or click to browse"}
        </span>

        {!uploading && (
          <span className="dropzone-hint">
            PDF files · Indexed locally
          </span>
        )}
      </label>

      {error && <div className="notice error">{error}</div>}
      {notice && <div className="notice success">{notice}</div>}

      <div className="library-toolbar">
        <div>
          <h3>Indexed documents</h3>
          <span className="document-count">
            {documents.length}{" "}
            {documents.length === 1 ? "document" : "documents"}
          </span>
        </div>

        <input
          className="document-search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search documents..."
          aria-label="Search documents"
        />
      </div>

      {loading ? (
        <div className="library-empty">Loading documents…</div>
      ) : filteredDocuments.length === 0 ? (
        <div className="library-empty">
          <div className="empty-document-icon">▤</div>
          <strong>
            {search ? "No matching documents" : "No documents yet"}
          </strong>
          <p>
            {search
              ? "Try another search term."
              : "Upload a PDF to start building your knowledge base."}
          </p>
        </div>
      ) : (
        <div className="document-list">
          {filteredDocuments.map((document) => (
            <article
              className="document-row"
              key={document.document_id}
            >
              <div className="pdf-icon">PDF</div>

              <div className="document-info">
                <strong title={document.document_name}>
                  {document.document_name}
                </strong>

                <div className="document-meta">
                  <span>{document.pages} pages</span>
                  <span>{document.chunks} chunks</span>
                </div>
              </div>

              <span className="indexed-status">
                <span className="status-dot" />
                Indexed
              </span>

              <button
                className="delete-button"
                onClick={() => handleDelete(document)}
                disabled={deletingId === document.document_id}
                aria-label={`Delete ${document.document_name}`}
                title="Delete document"
              >
                {deletingId === document.document_id
                  ? "Deleting…"
                  : "Delete"}
              </button>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

export default DocumentLibrary;
