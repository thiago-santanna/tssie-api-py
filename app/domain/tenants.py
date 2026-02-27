from pydantic import BaseModel
from typing import Optional, Dict, Any
from supabase import Client

class TenantBase(BaseModel):
    name: str
    instance_key: str
    segment: Optional[str] = None
    llm_provider: str = 'gemini'
    llm_model: str = 'gemini-1.5-flash'
    temperature: float = 0.0
    system_prompt_id: Optional[str] = None
    business_hours: Dict[str, Any] = {}
    integration_config: Dict[str, Any] = {}
    active: bool = True

class TenantCreate(TenantBase):
    pass

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    segment: Optional[str] = None
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    temperature: Optional[float] = None
    system_prompt_id: Optional[str] = None
    business_hours: Optional[Dict[str, Any]] = None
    integration_config: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None

def create_tenant(client: Client, tenant: TenantCreate) -> dict:
    data = tenant.model_dump(exclude_unset=True)
    response = client.table("tenants").insert(data).execute()
    if not response.data:
        raise Exception("Failed to create tenant")
    return response.data[0]

def get_tenant_by_instance_key(client: Client, instance_key: str) -> Optional[dict]:
    response = client.table("tenants").select("*").eq("instance_key", instance_key).execute()
    if response.data:
        return response.data[0]
    return None

def update_tenant(client: Client, tenant_id: str, tenant_update: TenantUpdate) -> dict:
    data = tenant_update.model_dump(exclude_unset=True)
    response = client.table("tenants").update(data).eq("id", tenant_id).execute()
    if not response.data:
        raise Exception("Failed to update or tenant not found")
    return response.data[0]
