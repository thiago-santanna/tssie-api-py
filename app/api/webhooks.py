from fastapi import APIRouter, Request, BackgroundTasks
from app.orchestration.pipeline import process_inbound_message

router = APIRouter()

@router.post("/evolution")
async def evolution_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook Oficial para Consumo da Evolution API (v2.x) configurado nas Instâncias do WhatsApp.
    O processamento roda em async background para dar instant "200 OK" para a Evolution.
    """
    payload = await request.json()
    
    # Entrega a thread pesada de Supabase e Mapeamento p/ Background Task do FastAPI
    background_tasks.add_task(process_inbound_message, payload)
    
    # Evolution Webhooks odeiam retornos pesados ou lentos, então a gente abraça e ignora.
    return {"status": "accepted"}
