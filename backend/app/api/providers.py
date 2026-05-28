"""Provider availability and status endpoints."""

import os
from typing import Dict

import httpx
from fastapi import APIRouter

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("/status", response_model=Dict[str, Dict])
async def get_provider_status():
    """
    Get availability status of all LLM providers.

    Returns:
        Dict with provider status and availability information

    Example:
        {
            "groq": {
                "available": true,
                "reason": "API key configured"
            },
            "openai": {
                "available": false,
                "reason": "API key not configured"
            },
            "anthropic": {
                "available": false,
                "reason": "API key not configured"
            },
            "ollama": {
                "available": false,
                "reason": "Service not running (disabled in this deployment)"
            }
        }
    """
    status = {}

    # Check Groq
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    status["groq"] = {
        "available": bool(groq_key),
        "reason": "API key configured" if groq_key else "API key not configured",
    }

    # Check OpenAI
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    status["openai"] = {
        "available": bool(openai_key),
        "reason": "API key configured" if openai_key else "API key not configured",
    }

    # Check Anthropic
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    status["anthropic"] = {
        "available": bool(anthropic_key),
        "reason": "API key configured" if anthropic_key else "API key not configured",
    }

    # Check Ollama - test if service is running
    ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{ollama_url}/api/tags", follow_redirects=True)
            ollama_available = response.status_code == 200
            ollama_reason = "Service is running" if ollama_available else "Service returned error"
    except (httpx.TimeoutException, httpx.ConnectError):
        ollama_available = False
        ollama_reason = "Service not running (disabled in this deployment)"
    except Exception:
        ollama_available = False
        ollama_reason = "Service unavailable"

    status["ollama"] = {"available": ollama_available, "reason": ollama_reason}

    return status
