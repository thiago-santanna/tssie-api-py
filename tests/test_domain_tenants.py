import pytest
from unittest.mock import MagicMock
from app.domain.tenants import create_tenant, get_tenant_by_instance_key, update_tenant, TenantCreate, TenantUpdate

def test_create_tenant_success():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [{"id": "uuid-123", "name": "Test", "instance_key": "inst-1"}]
    mock_client.table().insert().execute.return_value = mock_response

    tenant_in = TenantCreate(name="Test", instance_key="inst-1")
    result = create_tenant(mock_client, tenant_in)
    
    assert result["id"] == "uuid-123"
    assert result["name"] == "Test"
    mock_client.table.assert_called_with("tenants")

def test_create_tenant_failure():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = []
    mock_client.table().insert().execute.return_value = mock_response

    tenant_in = TenantCreate(name="Test", instance_key="inst-1")
    with pytest.raises(Exception, match="Failed to create tenant"):
        create_tenant(mock_client, tenant_in)

def test_get_tenant_by_instance_key():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [{"id": "uuid-123", "instance_key": "inst-1"}]
    mock_client.table().select().eq().execute.return_value = mock_response
    
    result = get_tenant_by_instance_key(mock_client, "inst-1")
    assert result["id"] == "uuid-123"

def test_update_tenant():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [{"id": "uuid-123", "name": "Updated"}]
    mock_client.table().update().eq().execute.return_value = mock_response
    
    update_in = TenantUpdate(name="Updated")
    result = update_tenant(mock_client, "uuid-123", update_in)
    
    assert result["name"] == "Updated"
    mock_client.table().update.assert_called()
