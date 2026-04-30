/**
 * API service for communicating with the backend.
 * @module services/api
 */

const API_URL = import.meta.env.VITE_API_URL || "https://social-media-production-0ef2.up.railway.app";

/**
 * Make a GET request and parse JSON response.
 * @param {string} path - API endpoint path
 * @returns {Promise<object>} JSON response
 * @throws {Error} If response is not OK
 */
async function getJson(path) {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  return response.json();
}

/**
 * List available messaging channels.
 * @returns {Promise<object>} Channels response
 */
export function listChannels() {
  return getJson("/messages/channels");
}

/**
 * List conversations for a specific channel.
 * @param {string} channel - Channel identifier
 * @returns {Promise<object>} Conversations response
 */
export function listConversations(channel) {
  return getJson(`/messages/conversations?channel=${encodeURIComponent(channel)}`);
}

/**
 * List messages for a conversation.
 * @param {number} conversationId - Conversation ID
 * @returns {Promise<object>} Messages response
 */
export function listMessages(conversationId) {
  return getJson(`/messages/conversations/${conversationId}/messages`);
}

/**
 * Send a message to a conversation.
 * @param {number} conversation_id - Conversation ID
 * @param {string} content - Message content
 * @returns {Promise<object>} Send response
 */
export async function sendMessage(conversation_id, content) {
  const response = await fetch(`${API_URL}/messages/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conversation_id, content }),
  });

  if (!response.ok) {
    throw new Error(`Send error: ${response.status}`);
  }

  return response.json();
}

/**
 * Get WebSocket URL for real-time updates.
 * @param {number} tenantId - Tenant ID
 * @returns {string} WebSocket URL
 */
export function getWebSocketUrl(tenantId = 1) {
  const wsBase = API_URL.replace("https://", "wss://").replace("http://", "ws://");
  return `${wsBase}/ws/${tenantId}`;
}

export { API_URL };