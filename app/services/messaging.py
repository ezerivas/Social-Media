import json
from typing import Dict, Any, Optional
from app.repositories.messages import MessageRepository
from app.channels.facebook import FacebookChannel
# Importar otros canales a medida que se implementen:
# from app.channels.whatsapp import WhatsAppChannel

class MessagingService:
    def __init__(self, db_pool, ws_manager=None):
        self.db_pool = db_pool
        self.ws_manager = ws_manager
        self.repository = MessageRepository(db_pool)
        
        # Registro de canales disponibles (Patrón Estrategia)
        self.channels = {
            "facebook": FacebookChannel(),
            # "whatsapp": WhatsAppChannel(),
        }

    async def handle_inbound_message(self, channel_name: str, payload: Dict[str, Any]):
        """
        Procesa mensajes que vienen desde las plataformas externas (Webhooks).
        """
        try:
            # 1. El adaptador del canal extrae la información estandarizada
            channel = self.channels.get(channel_name)
            if not channel:
                print(f"❌ Canal no soportado: {channel_name}")
                return

            message_data = channel.parse_webhook(payload)
            if not message_data:
                return # Eventos que no son mensajes (ej. entrega)

            # 2. Guardar en Base de Datos (Tenant, Conversación y Mensaje)
            # Nota: El repositorio maneja la lógica de crear conversación si no existe
            saved_message = await self.repository.save_message(
                tenant_id=message_data["tenant_id"],
                user_external_id=message_data["sender_id"],
                channel=channel_name,
                content=message_data["text"],
                role="user"
            )

            # 3. Notificar al Dashboard vía WebSockets en tiempo real
            if self.ws_manager:
                await self.ws_manager.broadcast_to_tenant(
                    message_data["tenant_id"],
                    {
                        "type": "new_message",
                        "data": saved_message
                    }
                )
            
            print(f"✅ Mensaje de {channel_name} procesado y guardado.")
            return saved_message

        except Exception as e:
            print(f"🔥 Error en handle_inbound_message: {str(e)}")
            raise e

    async def send_outbound_message(self, tenant_id: int, conversation_id: int, content: str):
        """
        Envía una respuesta desde el Dashboard hacia el cliente final.
        """
        try:
            # 1. Obtener detalles de la conversación y credenciales del canal
            conv = await self.repository.get_conversation_details(conversation_id)
            if not conv or conv["tenant_id"] != tenant_id:
                raise Exception("Conversación no encontrada o acceso denegado")

            channel_name = conv["channel"]
            external_user_id = conv["external_user_id"]
            
            # 2. Obtener configuración (tokens) del canal para este tenant
            channel_config = await self.repository.get_channel_config(tenant_id, channel_name)
            if not channel_config:
                raise Exception(f"Configuración no encontrada para el canal {channel_name}")

            # 3. Ejecutar el envío técnico a través de la API del proveedor
            channel_adapter = self.channels.get(channel_name)
            success = await channel_adapter.send_text(
                recipient_id=external_user_id,
                message_text=content,
                config=channel_config
            )

            if success:
                # 4. Guardar el mensaje del agente en la DB
                saved_message = await self.repository.save_outbound_message(
                    conversation_id=conversation_id,
                    content=content,
                    role="agent"
                )

                # 5. Notificar a otros dashboards abiertos del mismo tenant
                if self.ws_manager:
                    await self.ws_manager.broadcast_to_tenant(
                        tenant_id,
                        {
                            "type": "message_sent",
                            "data": saved_message
                        }
                    )
                return saved_message
            
            return None

        except Exception as e:
            print(f"🔥 Error en send_outbound_message: {str(e)}")
            raise e