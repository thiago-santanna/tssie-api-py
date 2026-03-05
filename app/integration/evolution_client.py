import httpx
from supabase import Client
import logging
from app.core.config import settings
from app.domain.events import create_outbound_event, OutboundEventCreate

logger = logging.getLogger(__name__)

async def send_whatsapp_message(supabase: Client, instance_key: str, remote_jid: str, text: str):
    # 1. Salvar evento no banco como PENDENTE de envio
    outbound_event = OutboundEventCreate(
        instance_key=instance_key, 
        remote_jid=remote_jid, 
        text=text
    )
    record = create_outbound_event(supabase, outbound_event)
    record_id = record["id"]
    
    # 2. Endpoints e headers baseados na documentação da Evolution API 2.x
    url = f"{settings.EVOLUTION_API_URL}/message/sendText/{instance_key}"
    headers = {
        "apikey": settings.EVOLUTION_GLOBAL_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "number": remote_jid,
        "text": text
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
        
        status = 'SENT' if response.status_code in (200, 201) else 'FAILED'
        error_msg = response.text if status == 'FAILED' else None
        
        # 3. Atualizar o evento Outbound com o status oficial que a API retornou
        supabase.table("outbound_events").update({
            "http_status": response.status_code,
            "send_status": status,
            "error_message": error_msg
        }).eq("id", record_id).execute()
        
        return response.json()
    except Exception as e:
        logger.error(f"Error sending message to {remote_jid} via Evolution: {e}")
        supabase.table("outbound_events").update({
            "send_status": "FAILED",
            "error_message": str(e)
        }).eq("id", record_id).execute()
        return None
