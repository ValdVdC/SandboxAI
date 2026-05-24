"""Real-time Multi-Provider Playground execution endpoints."""

import asyncio
import logging
import os
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.models import User
from app.schemas import (
    PlaygroundColumnResult,
    PlaygroundRunRequest,
    PlaygroundRunResponse,
)
from app.workers.tasks import _get_provider, cosine_similarity, get_embedding_model

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/playground", tags=["Playground"])


async def run_single_config(
    provider_name: str,
    model: str,
    prompt: str,
    expected: Optional[str],
    timeout: int,
) -> PlaygroundColumnResult:
    """Execute a prompt with a single provider and model."""
    start_time = time.time()
    try:
        provider_instance = _get_provider(provider_name)
        result = await provider_instance.execute(prompt, model, timeout)

        # Calculate semantic similarity if expected is provided
        score = None
        is_correct = None
        if expected and result.output:
            expected_norm = expected.lower().strip()
            output_norm = result.output.lower().strip()
            try:
                emb_model = get_embedding_model()
                embeddings = list(emb_model.embed([expected_norm, output_norm]))
                if len(embeddings) == 2:
                    similarity = cosine_similarity(embeddings[0], embeddings[1])
                    threshold = float(os.getenv("SEMANTIC_THRESHOLD", "0.8"))
                    score = max(0.0, min(1.0, similarity))
                    is_correct = score >= threshold
                else:
                    is_correct = (
                        expected_norm in output_norm or output_norm in expected_norm
                    )
                    score = 1.0 if is_correct else 0.0
            except Exception as eval_err:
                logger.error(f"Semantic evaluation failed in playground: {eval_err}")
                # Fallback to exact match substring
                is_correct = (
                    expected_norm in output_norm or output_norm in expected_norm
                )
                score = 1.0 if is_correct else 0.0

        latency_ms = (time.time() - start_time) * 1000

        return PlaygroundColumnResult(
            provider=provider_name,
            model=model,
            output=result.output,
            latency_ms=result.latency_ms,
            tokens_used=result.tokens_used,
            cost_usd=float(result.cost_usd),
            score=score,
            is_correct=is_correct,
            status="completed",
            error_message=None,
        )
    except Exception as exc:
        latency_ms = (time.time() - start_time) * 1000
        logger.error(f"Playground execution failed for {provider_name}/{model}: {exc}")
        return PlaygroundColumnResult(
            provider=provider_name,
            model=model,
            output=None,
            latency_ms=latency_ms,
            tokens_used=0,
            cost_usd=0.0,
            score=None,
            is_correct=None,
            status="failed",
            error_message=str(exc),
        )


@router.post("/run", response_model=PlaygroundRunResponse)
async def run_playground(
    request_data: PlaygroundRunRequest,
    user: User = Depends(get_current_user),
) -> PlaygroundRunResponse:
    """Execute a prompt template against up to 3 models/providers in parallel."""
    if len(request_data.configs) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A/B/C testing allows up to 3 configurations maximum.",
        )

    if len(request_data.configs) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specify at least 1 provider configuration.",
        )

    # 1. Jinja2 Prompt Interpolation
    final_prompt = request_data.prompt_content
    if request_data.input:
        import json

        from jinja2 import Template

        try:
            input_data = json.loads(request_data.input)
            if isinstance(input_data, dict):
                template = Template(request_data.prompt_content)
                final_prompt = template.render(**input_data)
            else:
                final_prompt = final_prompt.replace(
                    "{{input}}", str(request_data.input)
                )
                final_prompt = final_prompt.replace("{input}", str(request_data.input))
        except (json.JSONDecodeError, TypeError):
            final_prompt = final_prompt.replace("{{input}}", str(request_data.input))
            final_prompt = final_prompt.replace("{input}", str(request_data.input))

    timeout = int(os.getenv("MAX_CONTAINER_TIMEOUT", "60"))

    # 2. Run executions concurrently using asyncio.gather
    tasks = [
        run_single_config(
            provider_name=config.provider,
            model=config.model,
            prompt=final_prompt,
            expected=request_data.expected,
            timeout=timeout,
        )
        for config in request_data.configs
    ]

    results = await asyncio.gather(*tasks)

    return PlaygroundRunResponse(results=list(results))
