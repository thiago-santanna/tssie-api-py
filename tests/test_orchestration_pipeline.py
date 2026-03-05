import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.orchestration.pipeline import process_inbound_message

@patch("app.orchestration.pipeline.get_supabase")
@patch("app.orchestration.pipeline.get_tenant_by_instance_key")
@patch("app.orchestration.pipeline.create_inbound_event")
@patch("app.orchestration.pipeline.upsert_contact")
@patch("app.orchestration.pipeline.create_or_get_active_session")
@patch("app.orchestration.pipeline.send_whatsapp_message")
@patch("app.orchestration.pipeline.update_inbound_status")
@pytest.mark.asyncio
async def test_process_inbound_message_success(
    mock_update_inbound,
    mock_send_message,
    mock_session,
    mock_contact,
    mock_inbound,
    mock_tenant,
    mock_supabase
):
    mock_tenant.return_value = {"id": "tenant-1"}
    mock_inbound.return_value = {"id": "event-1"}
    mock_contact.return_value = {"id": "contact-1"}
    mock_session.return_value = {"id": "session-1"}
    
    payload = {
        "event": "messages.upsert",
        "instance": "TSSieDev",
        "data": {
            "message": {
                "key": {"remoteJid": "551199999999@s.whatsapp.net", "id": "msg-123", "fromMe": False},
                "pushName": "Test User"
            }
        }
    }
    
    result = await process_inbound_message(payload)
    
    assert result["status"] == "success"
    assert result["session_id"] == "session-1"
    
    mock_tenant.assert_called_once()
    mock_inbound.assert_called_once()
    mock_contact.assert_called_once()
    mock_session.assert_called_once()
    mock_send_message.assert_called_once()
    mock_update_inbound.assert_called_once()

@pytest.mark.asyncio
async def test_process_inbound_message_ignored_event():
    payload = {"event": "connection.update"}
    result = await process_inbound_message(payload)
    
    assert result["status"] == "ignored"
    assert "not a message upsert" in result["reason"]
