import { useEffect } from "react";

function Dashboard() {
  useEffect(() => {
    const socket = new WebSocket(
      "wss://social-media-production-0ef2.up.railway.app/ws/1"
    );

    socket.onopen = () => {
      console.log("🟢 Conectado");
      socket.send("hola desde frontend");
    };

    socket.onmessage = (event) => {
      console.log("📩 Mensaje:", event.data);
    };

    socket.onerror = (e) => {
      console.error("❌ Error:", e);
    };

    socket.onclose = () => {
      console.log("🔴 Cerrado");
    };

    return () => socket.close();
  }, []);

  return <h1>Probando WebSocket...</h1>;
}

export default Dashboard;