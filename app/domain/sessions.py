from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from supabase import Client

class SessionCreate(BaseModel):
    tenant_id: str
    contact_id: str
    remote_jid: str

def create_or_get_active_session(client: Client, session: SessionCreate) -> dict:
    # 1. find active session
    existing = client.table("sessions").select("*").eq("contact_id", session.contact_id).eq("status", "ACTIVE").execute()
    if existing.data:
        return existing.data[0]
    
    # 2. create if none
    data = session.model_dump()
    response = client.table("sessions").insert(data).execute()
    if not response.data:
        raise Exception("Failed to create session")
    return response.data[0]

def update_session_activity(client: Client, session_id: str, by_human: bool = False, by_bot: bool = False) -> dict:
    update_data = {"last_seen_at": datetime.now(timezone.utc).isoformat()}
    if by_human:
        update_data["last_human_message_at"] = update_data["last_seen_at"]
    if by_bot:
        update_data["last_bot_message_at"] = update_data["last_seen_at"]
        
    response = client.table("sessions").update(update_data).eq("id", session_id).execute()
    if not response.data:
        raise Exception("Session not found")
    return response.data[0]

def set_human_intervention(client: Client, session_id: str, active: bool) -> dict:
    response = client.table("sessions").update({"is_human_active": active}).eq("id", session_id).execute()
    if not response.data:
        raise Exception("Session not found")
    return response.data[0]
        
def close_session(client: Client, session_id: str) -> dict:
    response = client.table("sessions").update({"status": "CLOSED"}).eq("id", session_id).execute()
    if not response.data:
        raise Exception("Session not found")
    return response.data[0]
