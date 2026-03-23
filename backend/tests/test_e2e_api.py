"""E2E Tests for API Endpoints."""

import pytest
from sqlalchemy import select
from app.models import User, Prompt


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test the /health endpoint."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "sandboxai-api"
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test the / (root) endpoint."""
    response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data


@pytest.mark.asyncio
async def test_api_documentation_available(client):
    """Test that OpenAPI/Swagger documentation is available."""
    response = await client.get("/openapi.json")
    
    assert response.status_code == 200
    openapi = response.json()
    assert "openapi" in openapi
    assert openapi["info"]["title"] == "SandboxAI API"


@pytest.mark.asyncio
async def test_swagger_ui_endpoint(client):
    """Test that Swagger UI endpoint exists."""
    response = await client.get("/docs")
    
    assert response.status_code == 200
    # Should return HTML with Swagger UI
    assert "swagger" in response.text.lower()


@pytest.mark.asyncio
async def test_multiple_health_checks(client):
    """Test that health endpoint can be called multiple times."""
    for _ in range(5):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
