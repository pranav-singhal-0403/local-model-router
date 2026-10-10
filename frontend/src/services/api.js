
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

export async function sendChatMessage(query, topK = 5) {
  const response = await api.post("/chat", {
    query,
    top_k: topK,
  });

  return response.data;
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post(
    "/documents/upload",
    formData
  );

  return response.data;
}

export async function getDocuments() {
  const response = await api.get("/documents");
  return response.data;
}

export async function deleteDocument(documentId) {
  const response = await api.delete(
    `/documents/${encodeURIComponent(documentId)}`
  );

  return response.data;
}

export async function getHealth() {
  const response = await api.get("/health");
  return response.data;
}
