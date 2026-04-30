import { useEffect, useMemo, useRef, useState } from "react";
import {
  API_URL,
  listChannels,
  listConversations,
  listMessages,
  sendMessage,
} from "../services/api";

function Dashboard() {
  const [channels, setChannels] = useState([]);
  const [selectedChannel, setSelectedChannel] = useState("facebook");
  const [conversations, setConversations] = useState([]);
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [replyText, setReplyText] = useState("");
  const socketRef = useRef(null);

  const selectedConversation = useMemo(
    () => conversations.find((item) => item.id === selectedConversationId),
    [conversations, selectedConversationId]
  );

  useEffect(() => {
    listChannels().then(setChannels).catch(console.error);
  }, []);

  useEffect(() => {
    listConversations(selectedChannel)
      .then((data) => {
        const items = data.data || [];
        setConversations(items);
        setSelectedConversationId((prev) => prev ?? items[0]?.id ?? null);
      })
      .catch(console.error);
  }, [selectedChannel]);

  useEffect(() => {
    if (!selectedConversationId) {
      setMessages([]);
      return;
    }
    listMessages(selectedConversationId)
      .then((data) => setMessages(data.data || []))
      .catch(console.error);
  }, [selectedConversationId]);

  useEffect(() => {
    const socket = new WebSocket(`${API_URL.replace("https", "wss")}/ws/1`);
    socketRef.current = socket;

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (!["new_message", "message_sent"].includes(payload.type)) return;

        const incoming = payload.data;

        setConversations((prev) => {
          const exists = prev.some((c) => c.id === incoming.conversation_id);
          if (exists) {
            return prev.map((c) =>
              c.id === incoming.conversation_id
                ? {
                    ...c,
                    last_message: incoming.content,
                    last_message_role: incoming.role,
                    last_message_at: incoming.created_at,
                  }
                : c
            );
          }

          return [
            {
              id: incoming.conversation_id,
              channel: selectedChannel,
              external_user_id: "nuevo",
              last_message: incoming.content,
              last_message_role: incoming.role,
              last_message_at: incoming.created_at,
            },
            ...prev,
          ];
        });

        if (incoming.conversation_id === selectedConversationId) {
          setMessages((prev) => [...prev, incoming]);
        }
      } catch (error) {
        console.error("WS parse error", error);
      }
    };

    return () => socket.close();
  }, [selectedChannel, selectedConversationId]);

  const handleSend = async () => {
    if (!selectedConversationId || !replyText.trim()) return;
    try {
      await sendMessage(selectedConversationId, replyText.trim());
      setReplyText("");
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div style={styles.layout}>
      <aside style={styles.sidebar}>
        <h3>Canales</h3>
        {channels.map((channel) => (
          <button
            key={channel.id}
            onClick={() => setSelectedChannel(channel.id)}
            style={{
              ...styles.channelButton,
              opacity: channel.enabled ? 1 : 0.6,
              background: selectedChannel === channel.id ? "#1f2937" : "#111827",
            }}
          >
            {channel.name}
          </button>
        ))}
      </aside>

      <section style={styles.conversationList}>
        <h3>Conversaciones ({selectedChannel})</h3>
        {conversations.map((conversation) => (
          <button
            key={conversation.id}
            onClick={() => setSelectedConversationId(conversation.id)}
            style={{
              ...styles.conversationButton,
              background:
                selectedConversationId === conversation.id ? "#dbeafe" : "white",
            }}
          >
            <strong>{conversation.external_user_id}</strong>
            <small>{conversation.last_message}</small>
          </button>
        ))}
      </section>

      <section style={styles.chatSection}>
        <h3>
          {selectedConversation
            ? `Chat ${selectedConversation.external_user_id}`
            : "Selecciona una conversación"}
        </h3>
        <div style={styles.chatBox}>
          {messages.map((msg) => {
            const isOperator = msg.role === "agent";
            return (
              <div
                key={msg.id}
                style={{
                  ...styles.messageWrapper,
                  alignItems: isOperator ? "flex-end" : "flex-start",
                }}
              >
                <span style={styles.roleTag}>{isOperator ? "Operador" : "Usuario"}</span>
                <div
                  style={{
                    ...styles.message,
                    backgroundColor: isOperator ? "#1d4ed8" : "#374151",
                  }}
                >
                  {msg.content}
                </div>
              </div>
            );
          })}
        </div>
        <div style={styles.replyContainer}>
          <label style={styles.replyLabel}>Respuesta</label>
          <div style={styles.inputRow}>
          <input
            value={replyText}
            onChange={(e) => setReplyText(e.target.value)}
            placeholder="Responder conversación..."
            style={styles.input}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
          />
          <button onClick={handleSend} style={styles.sendButton} disabled={!selectedConversationId || !replyText.trim()}>
            Enviar
          </button>
        </div>
        </div>
      </section>
    </div>
  );
}

const styles = {
  layout: { display: "grid", gridTemplateColumns: "220px 300px 1fr", gap: 16, padding: 16 },
  sidebar: { background: "#111827", color: "white", padding: 12, borderRadius: 10 },
  channelButton: {
    width: "100%",
    color: "white",
    border: "1px solid #374151",
    borderRadius: 8,
    padding: 8,
    marginTop: 8,
    cursor: "pointer",
  },
  conversationList: { border: "1px solid #e5e7eb", borderRadius: 10, padding: 12, display: "flex", flexDirection: "column", gap: 8 },
  conversationButton: {
    textAlign: "left",
    border: "1px solid #e5e7eb",
    borderRadius: 8,
    padding: 10,
    cursor: "pointer",
    display: "flex",
    flexDirection: "column",
  },
  chatSection: { border: "1px solid #e5e7eb", borderRadius: 10, padding: 12, display: "flex", flexDirection: "column" },
  chatBox: { flex: 1, minHeight: 300, maxHeight: 450, overflowY: "auto", display: "flex", flexDirection: "column", gap: 8, background: "#111827", borderRadius: 8, padding: 10 },
  messageWrapper: { display: "flex", flexDirection: "column", maxWidth: "75%" },
  roleTag: { fontSize: 11, color: "#9ca3af", marginBottom: 4 },
  message: { color: "white", borderRadius: 8, padding: "8px 10px" },
  replyContainer: { marginTop: 10 },
  replyLabel: { fontSize: 13, color: "#374151", marginBottom: 6, display: "block" },
  inputRow: { display: "flex", gap: 8 },
  input: { flex: 1, padding: 10, borderRadius: 8, border: "1px solid #d1d5db" },
  sendButton: { padding: "10px 14px", borderRadius: 8, border: "none", background: "#2563eb", color: "white", cursor: "pointer" },
};

export default Dashboard;
