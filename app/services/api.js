const API_URL =
  import.meta.env.VITE_API_URL || "https://social-media-production-0ef2.up.railway.app";

async function getJson(path) {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Error API: ${response.status}`);
  }
  return response.json();
}

export function listChannels() {
  return getJson("/messages/channels");
}

export function listConversations(channel) {
  return getJson(`/messages/conversations?channel=${encodeURIComponent(channel)}`);
}

export function listMessages(conversationId) {
  return getJson(`/messages/conversations/${conversationId}/messages`);
}

export async function sendMessage(conversation_id, content) {
  const response = await fetch(`${API_URL}/messages/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conversation_id, content }),
  });

  if (!response.ok) {
    throw new Error(`Error enviando mensaje: ${response.status}`);
  }

  return response.json();
}

export function getWebSocketUrl(tenantId = 1) {
  const wsBase = API_URL.replace("https://", "wss://").replace("http://", "ws://");
  return `${wsBase}/ws/${tenantId}`;
}

export { API_URL };
