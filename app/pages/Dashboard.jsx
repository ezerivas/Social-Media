import { useEffect, useState } from "react";

function Dashboard() {
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const socket = new WebSocket(
      "wss://social-media-production-0ef2.up.railway.app/ws/1"
    );

    socket.onopen = () => {
      console.log("🟢 Conectado al WebSocket");
    };

    socket.onmessage = (event) => {
      console.log("📩 Mensaje recibido:", event.data);

      setMessages((prev) => [...prev, event.data]);
    };

    socket.onclose = () => {
      console.log("🔴 WebSocket cerrado");
    };

    return () => {
      socket.close();
    };
  }, []);

  return (
    <div>
      <h1>Dashboard en tiempo real</h1>

      {messages.map((msg, i) => (
        <p key={i}>{msg}</p>
      ))}
    </div>
  );
}

export default Dashboard;