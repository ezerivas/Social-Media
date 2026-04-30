import { useEffect, useRef, useState } from "react";

function Dashboard() {
  const socketRef = useRef(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  useEffect(() => {
    // 🔌 conectar WebSocket
    const socket = new WebSocket(
      "wss://social-media-production-0ef2.up.railway.app/ws/1"
    );

    socketRef.current = socket;

    // 🟢 conexión abierta
    socket.onopen = () => {
      console.log("🟢 conectado");
      socket.send("frontend conectado");
    };

    // 📩 recibir mensajes
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        setMessages((prev) => [
          ...prev,
          {
            text: data.data,
            type: "received",
          },
        ]);
      } catch (e) {
        console.log("error parse:", event.data);
      }
    };

    // ❌ error
    socket.onerror = (err) => {
      console.error("❌ error websocket", err);
    };

    // 🔴 cierre
    socket.onclose = () => {
      console.log("🔴 desconectado");
    };

    return () => socket.close();
  }, []);

  // 📤 enviar mensaje
  const sendMessage = () => {
    if (!input.trim()) return;

    const msg = {
      text: input,
      type: "sent",
    };

    // mostrar en UI
    setMessages((prev) => [...prev, msg]);

    // enviar al backend
    socketRef.current?.send(input);

    setInput("");
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>💬 Chat en tiempo real</h2>

      {/* mensajes */}
      <div style={styles.chatBox}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              ...styles.message,
              alignSelf: msg.type === "sent" ? "flex-end" : "flex-start",
              backgroundColor: msg.type === "sent" ? "#4caf50" : "#333",
            }}
          >
            {msg.text}
          </div>
        ))}
      </div>

      {/* input */}
      <div style={styles.inputBox}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Escribí un mensaje..."
          style={styles.input}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button onClick={sendMessage} style={styles.button}>
          Enviar
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: 600,
    margin: "0 auto",
    fontFamily: "Arial",
  },
  title: {
    textAlign: "center",
  },
  chatBox: {
    height: 400,
    border: "1px solid #ccc",
    borderRadius: 10,
    padding: 10,
    display: "flex",
    flexDirection: "column",
    overflowY: "auto",
    backgroundColor: "#111",
    color: "#fff",
  },
  message: {
    padding: 10,
    borderRadius: 10,
    margin: "5px 0",
    maxWidth: "70%",
  },
  inputBox: {
    display: "flex",
    marginTop: 10,
  },
  input: {
    flex: 1,
    padding: 10,
    borderRadius: 5,
    border: "1px solid #ccc",
  },
  button: {
    marginLeft: 10,
    padding: "10px 20px",
    backgroundColor: "#2196f3",
    color: "#fff",
    border: "none",
    borderRadius: 5,
    cursor: "pointer",
  },
};

export default Dashboard;