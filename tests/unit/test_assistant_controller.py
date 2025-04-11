import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import status

from app.controllers import assistant_controller
from app.models.assistant import Assistant
from app.schemas.assistant import AssistantCreate, AssistantUpdate


@pytest.mark.asyncio
async def test_create_assistant():
    """
    Test creating an assistant.
    """
    # Mock data
    assistant_data = {"name": "Test Assistant", "description": "Test description"}
    assistant_in = AssistantCreate(**assistant_data)
    
    # Mock the database session
    mock_db = MagicMock()
    
    # Mock the create_item function
    mock_assistant = MagicMock(spec=Assistant)
    mock_assistant.to_dict.return_value = {
        "id": 1, 
        "name": "Test Assistant", 
        "description": "Test description",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }
    
    with patch("app.controllers.assistant_controller.create_item", new=AsyncMock(return_value=mock_assistant)) as mock_create:
        response = await assistant_controller.create(assistant_in, mock_db)
        
        # Check that create_item was called with correct arguments
        mock_create.assert_called_once_with(mock_db, Assistant, assistant_data)
        
        # Check the response
        assert response.status_code == status.HTTP_201_CREATED
        assert response.body.decode() == '{"ok":true,"payload":{"id":1,"name":"Test Assistant","description":"Test description","created_at":"2023-01-01T00:00:00","updated_at":"2023-01-01T00:00:00"}}'


@pytest.mark.asyncio
async def test_update_assistant():
    """
    Test updating an assistant.
    """
    # Mock data
    assistant_id = "1"
    update_data = {"description": "Updated description"}
    assistant_update = AssistantUpdate(**update_data)
    
    # Mock the database session
    mock_db = AsyncMock()
    
    # Mock the is_id_valid function
    mock_valid_id = 1
    
    # Mock the update_item function
    mock_assistant = MagicMock(spec=Assistant)
    mock_assistant.to_dict.return_value = {
        "id": 1, 
        "name": "Test Assistant", 
        "description": "Updated description",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }
    
    with patch("app.controllers.assistant_controller.is_id_valid", return_value=mock_valid_id) as mock_id_valid, \
         patch("app.controllers.assistant_controller.update_item", new=AsyncMock(return_value=mock_assistant)) as mock_update:
        response = await assistant_controller.update(assistant_id, assistant_update, mock_db)
        
        # Check that the functions were called with correct arguments
        mock_id_valid.assert_called_once_with(assistant_id)
        mock_update.assert_called_once_with(mock_db, Assistant, mock_valid_id, update_data)
        
        # Check the response
        assert response.status_code == status.HTTP_200_OK
        assert response.body.decode() == '{"ok":true,"payload":{"id":1,"name":"Test Assistant","description":"Updated description","created_at":"2023-01-01T00:00:00","updated_at":"2023-01-01T00:00:00"}}'


@pytest.mark.asyncio
async def test_update_nonexistent_assistant():
    """
    Test updating a nonexistent assistant.
    """
    # Mock data
    assistant_id = "1"
    update_data = {"description": "Updated description"}
    assistant_update = AssistantUpdate(**update_data)
    
    # Mock the database session
    mock_db = AsyncMock()
    
    # Mock the is_id_valid function
    mock_valid_id = 1
    
    # Mock the update_item function to return None (assistant not found)
    with patch("app.controllers.assistant_controller.is_id_valid", return_value=mock_valid_id) as mock_id_valid, \
         patch("app.controllers.assistant_controller.update_item", new=AsyncMock(return_value=None)) as mock_update:
        response = await assistant_controller.update(assistant_id, assistant_update, mock_db)
        
        # Check that the functions were called with correct arguments
        mock_id_valid.assert_called_once_with(assistant_id)
        mock_update.assert_called_once_with(mock_db, Assistant, mock_valid_id, update_data)
        
        # Check the response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert '"errors":' in response.body.decode()
        assert '"ok":false' in response.body.decode()


@pytest.mark.asyncio
async def test_delete_assistant():
    """
    Test deleting an assistant.
    """
    # Mock data
    assistant_id = "1"
    
    # Mock the database session
    mock_db = AsyncMock()
    
    # Mock the is_id_valid function
    mock_valid_id = 1
    
    # Mock the delete_item function
    mock_assistant = MagicMock(spec=Assistant)
    
    with patch("app.controllers.assistant_controller.is_id_valid", return_value=mock_valid_id) as mock_id_valid, \
         patch("app.controllers.assistant_controller.delete_item", new=AsyncMock(return_value=mock_assistant)) as mock_delete:
        response = await assistant_controller.delete(assistant_id, mock_db)
        
        # Check that the functions were called with correct arguments
        mock_id_valid.assert_called_once_with(assistant_id)
        mock_delete.assert_called_once_with(mock_db, Assistant, mock_valid_id)
        
        # Check the response
        assert response.status_code == status.HTTP_200_OK
        assert response.body.decode() == '{"ok":true,"message":"Assistant deleted successfully"}'


@pytest.mark.asyncio
async def test_delete_nonexistent_assistant():
    """
    Test deleting a nonexistent assistant.
    """
    # Mock data
    assistant_id = "1"
    
    # Mock the database session
    mock_db = AsyncMock()
    
    # Mock the is_id_valid function
    mock_valid_id = 1
    
    # Mock the delete_item function to return None (assistant not found)
    with patch("app.controllers.assistant_controller.is_id_valid", return_value=mock_valid_id) as mock_id_valid, \
         patch("app.controllers.assistant_controller.delete_item", new=AsyncMock(return_value=None)) as mock_delete:
        response = await assistant_controller.delete(assistant_id, mock_db)
        
        # Check that the functions were called with correct arguments
        mock_id_valid.assert_called_once_with(assistant_id)
        mock_delete.assert_called_once_with(mock_db, Assistant, mock_valid_id)
        
        # Check the response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert '"errors":' in response.body.decode()
        assert '"ok":false' in response.body.decode()


@pytest.mark.asyncio
async def test_get_one_assistant():
    """
    Test getting an assistant by ID.
    """
    # Mock data
    assistant_id = "1"
    
    # Mock the database session
    mock_db = AsyncMock()
    
    # Mock the is_id_valid function
    mock_valid_id = 1
    
    # Mock the get_item function
    mock_assistant = MagicMock(spec=Assistant)
    mock_assistant.to_dict.return_value = {
        "id": 1, 
        "name": "Test Assistant", 
        "description": "Test description",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }
    
    with patch("app.controllers.assistant_controller.is_id_valid", return_value=mock_valid_id) as mock_id_valid, \
         patch("app.controllers.assistant_controller.get_item", new=AsyncMock(return_value=mock_assistant)) as mock_get:
        response = await assistant_controller.get_one(assistant_id, mock_db)
        
        # Check that the functions were called with correct arguments
        mock_id_valid.assert_called_once_with(assistant_id)
        mock_get.assert_called_once_with(mock_db, Assistant, mock_valid_id)
        
        # Check the response
        assert response.status_code == status.HTTP_200_OK
        assert response.body.decode() == '{"ok":true,"payload":{"id":1,"name":"Test Assistant","description":"Test description","created_at":"2023-01-01T00:00:00","updated_at":"2023-01-01T00:00:00"}}'


@pytest.mark.asyncio
async def test_get_nonexistent_assistant():
    """
    Test getting a nonexistent assistant.
    """
    # Mock data
    assistant_id = "1"
    
    # Mock the database session
    mock_db = AsyncMock()
    
    # Mock the is_id_valid function
    mock_valid_id = 1
    
    # Mock the get_item function to return None (assistant not found)
    with patch("app.controllers.assistant_controller.is_id_valid", return_value=mock_valid_id) as mock_id_valid, \
         patch("app.controllers.assistant_controller.get_item", new=AsyncMock(return_value=None)) as mock_get:
        response = await assistant_controller.get_one(assistant_id, mock_db)
        
        # Check that the functions were called with correct arguments
        mock_id_valid.assert_called_once_with(assistant_id)
        mock_get.assert_called_once_with(mock_db, Assistant, mock_valid_id)
        
        # Check the response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert '"errors":' in response.body.decode()
        assert '"ok":false' in response.body.decode()


@pytest.mark.asyncio
async def test_list_all_assistants():
    """
    Test listing all assistants.
    """
    # Mock data
    mock_request = MagicMock()
    
    # Mock the database session
    mock_db = AsyncMock()
    
    # Mock the get_all_items function
    mock_assistants = [MagicMock(spec=Assistant), MagicMock(spec=Assistant)]
    mock_assistants[0].to_dict.return_value = {
        "id": 1, 
        "name": "Assistant 1", 
        "description": "Description 1",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }
    mock_assistants[1].to_dict.return_value = {
        "id": 2, 
        "name": "Assistant 2", 
        "description": "Description 2",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }
    
    with patch("app.controllers.assistant_controller.get_all_items", new=AsyncMock(return_value=mock_assistants)) as mock_get_all:
        response = await assistant_controller.list_all(mock_request, mock_db)
        
        # Check that get_all_items was called with correct arguments
        mock_get_all.assert_called_once_with(mock_db, Assistant)
        
        # Check the response
        assert response.status_code == status.HTTP_200_OK
        response_data = response.body.decode()
        assert '"ok":true' in response_data
        assert '"payload":[' in response_data
        assert '"id":1' in response_data
        assert '"id":2' in response_data


@pytest.mark.asyncio
async def test_list_paginated_assistants():
    """
    Test listing assistants with pagination.
    """
    # Mock data
    mock_request = MagicMock()
    mock_request.query_params = {"page": "1", "size": "10"}
    
    # Mock the database session
    mock_db = AsyncMock()
    
    # Mock the functions
    mock_processed_query = {"page": 1, "size": 10}
    
    # Mock pagination result
    class MockPaginationResult:
        def __init__(self):
            self.items = [MagicMock(spec=Assistant), MagicMock(spec=Assistant)]
            self.total = 2
            self.page = 1
            self.size = 10
            self.pages = 1
    
    mock_pagination = MockPaginationResult()
    mock_pagination.items[0].to_dict.return_value = {
        "id": 1, 
        "name": "Assistant 1", 
        "description": "Description 1",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }
    mock_pagination.items[1].to_dict.return_value = {
        "id": 2, 
        "name": "Assistant 2", 
        "description": "Description 2",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }
    
    with patch("app.controllers.assistant_controller.check_query_string", new=AsyncMock(return_value=mock_processed_query)) as mock_check_query, \
         patch("app.controllers.assistant_controller.get_items", new=AsyncMock(return_value=mock_pagination)) as mock_get_items:
        response = await assistant_controller.list_paginated(mock_request, mock_db)
        
        # Check that the functions were called with correct arguments
        mock_check_query.assert_called_once_with({"page": "1", "size": "10"})
        mock_get_items.assert_called_once_with(mock_db, Assistant, mock_request, mock_processed_query)
        
        # Check the response
        assert response.status_code == status.HTTP_200_OK
        response_data = response.body.decode()
        assert '"ok":true' in response_data
        assert '"items":[' in response_data
        assert '"total":2' in response_data
        assert '"page":1' in response_data
        assert '"size":10' in response_data
        assert '"pages":1' in response_data 