import pytest
from unittest.mock import MagicMock
from app.domain.contacts import upsert_contact, get_contact, update_contact_status, ContactCreate

def test_upsert_contact_success():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [{"id": "contact-123", "remote_jid": "5511999999999@s.whatsapp.net"}]
    mock_client.table().upsert().execute.return_value = mock_response
    
    contact_in = ContactCreate(tenant_id="tenant-1", remote_jid="5511999999999@s.whatsapp.net")
    result = upsert_contact(mock_client, contact_in)
    
    assert result["id"] == "contact-123"
    mock_client.table.assert_called_with("contacts")

def test_get_contact_found():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [{"id": "contact-123", "status": "LEAD"}]
    mock_client.table().select().eq().eq().execute.return_value = mock_response
    
    result = get_contact(mock_client, "tenant-1", "5511999999999@s.whatsapp.net")
    assert result["id"] == "contact-123"

def test_update_contact_status():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [{"id": "contact-123", "status": "QUALIFIED"}]
    mock_client.table().update().eq().execute.return_value = mock_response
    
    result = update_contact_status(mock_client, "contact-123", status="QUALIFIED", tags=["vip"])
    assert result["status"] == "QUALIFIED"
    mock_client.table().update.assert_called_with({"status": "QUALIFIED", "tags": ["vip"]})
