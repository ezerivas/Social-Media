import { useEffect, useRef } from "react";

function Dashboard() {
  // Guardamos el socket para poder reutilizarlo si hace falta
  const socketRef = useRef(null);

  useEffect(() => {
    // 🔌 Conexión al WebSocket del backend (Railway)
    const socket = new WebSocket(
      "wss://social-media-production-0ef2.up.railway.app/ws/1"
    );

    socketRef.current = socket;

    // 🟢 Cuando conecta correctamente
    socket.onopen = () => {
      console.log("🟢 Conectado al WebSocket");

      // mensaje de prueba al backend
      socket.send("hola desde frontend");
    };

    // 📩 Cuando llega un mensaje del servidor
    socket.onmessage = (event) => {
      console.log("📩 Mensaje recibido:", event.data);

      // Si el backend manda JSON, lo podés parsear así:
      // const data = JSON.parse(event.data);
    };

    // ❌ Errores de conexión
    socket.onerror = (error) => {
      console.error("❌ Error WebSocket:", error);
    };

    // 🔴 Cuando se cierra la conexión
    socket.onclose = () => {
      console.log("🔴 WebSocket cerrado");
    };

    // 🧹 Cleanup al salir del componente
    return () => {
      socket.close();
    };
  }, []);

  return (
    <div>
      <h1>Dashboard WebSocket en tiempo real</h1>
    </div>
  );
}

export default Dashboard;