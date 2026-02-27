from pydantic import BaseModel
from typing import Optional
from supabase import Client

class ContactCreate(BaseModel):
    tenant_id: str
    remote_jid: str
    push_name: Optional[str] = None
    status: str = 'LEAD'
    tags: list = []

class ContactUpdate(BaseModel):
    push_name: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[list] = None

def upsert_contact(client: Client, contact: ContactCreate) -> dict:
    data = contact.model_dump(exclude_unset=True)
    response = client.table("contacts").upsert(data, on_conflict="tenant_id,remote_jid").execute()
    if not response.data:
        raise Exception("Failed to upsert contact")
    return response.data[0]

def get_contact(client: Client, tenant_id: str, remote_jid: str) -> Optional[dict]:
    response = client.table("contacts").select("*").eq("tenant_id", tenant_id).eq("remote_jid", remote_jid).execute()
    if response.data:
        return response.data[0]
    return None

def update_contact_status(client: Client, contact_id: str, status: str, tags: Optional[list] = None) -> dict:
    update_data = {"status": status}
    if tags is not None:
        update_data["tags"] = tags
    response = client.table("contacts").update(update_data).eq("id", contact_id).execute()
    if not response.data:
        raise Exception("Contact not found or update failed")
    return response.data[0]
