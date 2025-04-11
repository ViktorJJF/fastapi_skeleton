import pytest
from fastapi import Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant import Assistant
from app.utils.db_helpers import (
    get_all_items,
    get_items,
    get_item,
    create_item,
    update_item,
    delete_item,
    check_query_string
)


@pytest.mark.asyncio
async def test_create_and_get_item(test_db: AsyncSession):
    """
    Test creating and then retrieving an item.
    """
    # Create a test assistant
    assistant_data = {
        "name": "Test Assistant",
        "description": "Test description"
    }
    
    # Create the item
    created_assistant = await create_item(test_db, Assistant, assistant_data)
    
    # Verify the item was created correctly
    assert created_assistant is not None
    assert created_assistant.name == "Test Assistant"
    assert created_assistant.description == "Test description"
    assert created_assistant.id is not None
    
    # Get the item by ID
    retrieved_assistant = await get_item(test_db, Assistant, created_assistant.id)
    
    # Verify the item was retrieved correctly
    assert retrieved_assistant is not None
    assert retrieved_assistant.id == created_assistant.id
    assert retrieved_assistant.name == created_assistant.name
    assert retrieved_assistant.description == created_assistant.description


@pytest.mark.asyncio
async def test_update_item(test_db: AsyncSession):
    """
    Test updating an item.
    """
    # Create a test assistant
    assistant_data = {
        "name": "Update Test Assistant",
        "description": "Original description"
    }
    
    # Create the item
    created_assistant = await create_item(test_db, Assistant, assistant_data)
    
    # Update the item
    update_data = {
        "description": "Updated description"
    }
    updated_assistant = await update_item(test_db, Assistant, created_assistant.id, update_data)
    
    # Verify the item was updated correctly
    assert updated_assistant is not None
    assert updated_assistant.id == created_assistant.id
    assert updated_assistant.name == created_assistant.name  # Should be unchanged
    assert updated_assistant.description == "Updated description"  # Should be updated
    
    # Get the item to verify it was updated in the database
    retrieved_assistant = await get_item(test_db, Assistant, created_assistant.id)
    assert retrieved_assistant.description == "Updated description"


@pytest.mark.asyncio
async def test_delete_item(test_db: AsyncSession):
    """
    Test deleting an item.
    """
    # Create a test assistant
    assistant_data = {
        "name": "Delete Test Assistant",
        "description": "To be deleted"
    }
    
    # Create the item
    created_assistant = await create_item(test_db, Assistant, assistant_data)
    
    # Delete the item
    deleted_assistant = await delete_item(test_db, Assistant, created_assistant.id)
    
    # Verify the item was returned by delete_item
    assert deleted_assistant is not None
    assert deleted_assistant.id == created_assistant.id
    
    # Verify the item is no longer in the database
    retrieved_assistant = await get_item(test_db, Assistant, created_assistant.id)
    assert retrieved_assistant is None


@pytest.mark.asyncio
async def test_get_all_items(test_db: AsyncSession):
    """
    Test retrieving all items.
    """
    # Create some test assistants
    for i in range(3):
        await create_item(test_db, Assistant, {
            "name": f"List Test Assistant {i}",
            "description": f"For testing get_all_items {i}"
        })
    
    # Get all assistants
    assistants = await get_all_items(test_db, Assistant)
    
    # Verify we got at least 3 assistants
    assert len(assistants) >= 3
    
    # Verify they have the correct structure
    for assistant in assistants:
        assert isinstance(assistant, Assistant)
        assert hasattr(assistant, "id")
        assert hasattr(assistant, "name")
        assert hasattr(assistant, "description")


@pytest.mark.asyncio
async def test_get_items_pagination(test_db: AsyncSession):
    """
    Test retrieving items with pagination.
    """
    # Clear any existing assistants to have a clean test
    existing_assistants = await get_all_items(test_db, Assistant)
    for assistant in existing_assistants:
        await delete_item(test_db, Assistant, assistant.id)
    
    # Create a set of test assistants
    for i in range(5):
        await create_item(test_db, Assistant, {
            "name": f"Pagination Test Assistant {i}",
            "description": f"For testing pagination {i}"
        })
    
    # Create a mock request
    mock_request = Request({"type": "http"})
    
    # Test pagination with different parameters
    query_params = {
        "page": 1,
        "size": 2
    }
    
    # Get paginated items
    result = await get_items(test_db, Assistant, mock_request, query_params)
    
    # Verify pagination properties
    assert result.page == 1
    assert result.size == 2
    assert result.total >= 5
    assert len(result.items) == 2
    assert result.pages >= 3  # At least 3 pages with 5 items and page size 2
    
    # Test second page
    query_params["page"] = 2
    result = await get_items(test_db, Assistant, mock_request, query_params)
    
    # Verify pagination properties for second page
    assert result.page == 2
    assert result.size == 2
    assert len(result.items) == 2


@pytest.mark.asyncio
async def test_check_query_string():
    """
    Test the check_query_string function.
    """
    # Test with page and size parameters
    query_params = {
        "page": "2",
        "size": "10"
    }
    
    result = await check_query_string(query_params)
    
    # Verify the parameters were converted correctly
    assert result["page"] == 2
    assert result["size"] == 10
    
    # Test with additional parameters
    query_params = {
        "page": "1",
        "size": "20",
        "sort": "name",
        "order": "asc"
    }
    
    result = await check_query_string(query_params)
    
    # Verify all parameters are present
    assert result["page"] == 1
    assert result["size"] == 20
    assert result["sort"] == "name"
    assert result["order"] == "asc"
    
    # Test with invalid page parameter
    query_params = {
        "page": "invalid",
        "size": "10"
    }
    
    result = await check_query_string(query_params)
    
    # Verify default value is used for invalid page
    assert result["page"] == 1
    assert result["size"] == 10 