import { useState } from "react";

import { uploadDocument } from "../services/api";


function UploadPanel() {

  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");


  async function handleUpload() {

    if (!file) {
      return;
    }

    try {

      setUploading(true);
      setMessage("");

      const result = await uploadDocument(file);

      setMessage(
        `${result.filename} indexed successfully.`
      );

      setFile(null);

    } catch (error) {

      setMessage(
        error.response?.data?.detail ||
        "Document upload failed."
      );

    } finally {

      setUploading(false);

    }
  }


  return (
    <div className="upload-panel">

      <input
        type="file"
        accept=".pdf"
        onChange={(event) =>
          setFile(
            event.target.files?.[0] || null
          )
        }
      />

      <button
        onClick={handleUpload}
        disabled={!file || uploading}
      >
        {uploading
          ? "Indexing..."
          : "Upload PDF"}
      </button>

      {message && (
        <div className="upload-message">
          {message}
        </div>
      )}

    </div>
  );
}


export default UploadPanel;