import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
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

export async function getHealth() {
  const response = await api.get("/health");

  return response.data;
}