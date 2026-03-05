from pydantic import BaseModel
from typing import Optional, Dict, Any
from supabase import Client

class InboundEventCreate(BaseModel):
    message_id: str
    instance_key: str
    remote_jid: str
    raw_payload: Dict[str, Any]
    processing_status: str = 'PENDING'

class OutboundEventCreate(BaseModel):
    instance_key: str
    remote_jid: str
    text: str
    http_status: Optional[int] = None
    send_status: str = 'PENDING'
    error_message: Optional[str] = None

def create_inbound_event(client: Client, event: InboundEventCreate) -> dict:
    data = event.model_dump()
    response = client.table("inbound_events").insert(data).execute()
    if not response.data:
        raise Exception("Failed to insert inbound event")
    return response.data[0]

def update_inbound_status(client: Client, event_id: str, status: str) -> dict:
    response = client.table("inbound_events").update({"processing_status": status}).eq("id", event_id).execute()
    if not response.data:
        raise Exception("Event not found")
    return response.data[0]

def create_outbound_event(client: Client, event: OutboundEventCreate) -> dict:
    data = event.model_dump(exclude_unset=True)
    response = client.table("outbound_events").insert(data).execute()
    if not response.data:
        raise Exception("Failed to insert outbound event")
    return response.data[0]
