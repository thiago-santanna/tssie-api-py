import pytest
from unittest.mock import MagicMock
from app.domain.sessions import (
    create_or_get_active_session, 
    update_session_activity, 
    set_human_intervention, 
    close_session,
    SessionCreate
)

def test_create_or_get_active_session_existing():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [{"id": "session-123", "status": "ACTIVE"}]
    mock_client.table().select().eq().eq().execute.return_value = mock_response
    
    session_in = SessionCreate(tenant_id="t1", contact_id="c1", remote_jid="5511")
    result = create_or_get_active_session(mock_client, session_in)
    
    assert result["id"] == "session-123"
    # Como achou as sessão ativa, não deve chamar o insert
    mock_client.table().insert.assert_not_called()

def test_create_or_get_active_session_new():
    mock_client = MagicMock()
    mock_select_response = MagicMock()
    mock_select_response.data = [] # Nenhuma sessão ativa = array vazio
    
    mock_insert_response = MagicMock()
    mock_insert_response.data = [{"id": "session-new", "status": "ACTIVE"}]
    
    mock_client.table().select().eq().eq().execute.return_value = mock_select_response
    mock_client.table().insert().execute.return_value = mock_insert_response
    
    session_in = SessionCreate(tenant_id="t1", contact_id="c1", remote_jid="5511")
    result = create_or_get_active_session(mock_client, session_in)
    
    assert result["id"] == "session-new"
    mock_client.table().insert.assert_called_with(session_in.model_dump())

def test_update_session_activity():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [{"id": "session-123", "last_seen_at": "timestamp"}]
    mock_client.table().update().eq().execute.return_value = mock_response
    
    result = update_session_activity(mock_client, "session-123", by_bot=True)
    assert "last_seen_at" in result
    update_call_args = mock_client.table().update.call_args[0][0]
    # Certificamos que atualizou de fato atrelando a bot interaction
    assert "last_bot_message_at" in update_call_args
    assert "last_human_message_at" not in update_call_args

def test_close_session():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [{"id": "session-123", "status": "CLOSED"}]
    mock_client.table().update().eq().execute.return_value = mock_response
    
    result = close_session(mock_client, "session-123")
    assert result["status"] == "CLOSED"
