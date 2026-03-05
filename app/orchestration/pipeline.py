from app.core.dependencies import get_supabase
from app.domain.tenants import get_tenant_by_instance_key
from app.domain.contacts import upsert_contact, ContactCreate
from app.domain.sessions import create_or_get_active_session, SessionCreate
from app.domain.events import create_inbound_event, update_inbound_status, InboundEventCreate
from app.integration.evolution_client import send_whatsapp_message
import logging

logger = logging.getLogger(__name__)

async def process_inbound_message(payload: dict):
    """
    Recebe um payload da Evolution API, normaliza e persiste dados da Sprint 3.
    """
    supabase = get_supabase()
    instance_key = payload.get("instance", "")
    event_type = payload.get("event", "")
    data = payload.get("data", {})
    
    # Por ora, lidamos apenas com novidades de mensagens
    if event_type != "messages.upsert":
        return {"status": "ignored", "reason": "not a message upsert. Event type: " + event_type}
    
    message = data.get("message", {}) if isinstance(data, dict) else {}
    if not message:
        return {"status": "ignored", "reason": "no message body found in payload"}

    # Evolution API formatação 
    msg_key = message.get("key", {})
    remote_jid = msg_key.get("remoteJid", "")
    message_id = msg_key.get("id", "")
    from_me = msg_key.get("fromMe", False)
    push_name = message.get("pushName", "Contato")
    
    # Evitar loops em que o TSSie lê as próprias mensagens ou status defaults
    if from_me or "status@broadcast" in remote_jid or not remote_jid:
        return {"status": "ignored", "reason": "invalid remote_jid or from_me"}
    
    # 1. Encontrar o Tenant (Empresa SaaS) responsável por processar essa rota
    tenant = get_tenant_by_instance_key(supabase, instance_key)
    if not tenant:
        logger.warning(f"Tenant for instance key '{instance_key}' not discovered in db.")
        return {"status": "ignored", "reason": "tenant not found"}
        
    tenant_id = tenant["id"]

    # 2. Salvar Audit Trail / Inbound Event no Supabase
    inbound_event = InboundEventCreate(
        message_id=message_id,
        instance_key=instance_key,
        remote_jid=remote_jid,
        raw_payload=payload
    )
    
    try:
        event_record = create_inbound_event(supabase, inbound_event)
    except Exception as e:
        logger.error(f"Duplicated or rejected inbound_event. MessageID {message_id}: {str(e)}")
        return {"status": "error", "reason": str(e)}

    # 3. Cria ou Atualiza Lead (Contact)
    contact_in = ContactCreate(tenant_id=tenant_id, remote_jid=remote_jid, push_name=push_name)
    contact = upsert_contact(supabase, contact_in)
    
    # 4. Cria ou Retoma Sessão (Workflow Híbrido Bot/Humano)
    session_in = SessionCreate(tenant_id=tenant_id, contact_id=contact["id"], remote_jid=remote_jid)
    session = create_or_get_active_session(supabase, session_in)
    
    # 5. [Sprint 3 Action] Enviar uma Resposta Hardcoded de "Olá!" provando E2E Integrado 
    reply_text = f"Beep-Boop! Olá {push_name or ''}! O TSSie reconheceu seu número ({remote_jid}) chegando pela porta {instance_key} na nossa Sprint 3. Eu já marquei essa rota em minha base para você!"
    await send_whatsapp_message(supabase, instance_key, remote_jid, reply_text)
    
    # 6. Marcar inbound como devidamente navegado e processado
    update_inbound_status(supabase, event_record["id"], "PROCESSED")
    
    return {"status": "success", "session_id": session["id"]}
