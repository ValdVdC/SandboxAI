"""
📋 Celery Tasks — SandboxAI

Tarefas assíncronas para execução de testes de prompts em containers.
"""

from celery import shared_task
from .celery_app import app
import logging

# Re-exportar app para que celery CLI encontre: celery -A app.worker.tasks
__all__ = ["app", "execute_test"]

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="execute_test")
def execute_test(self, prompt_id: str, version: int, input_data: str):
    """
    Executa um teste de prompt em um container isolado.

    Args:
        prompt_id: ID do prompt
        version: Número da versão
        input_data: Dados de entrada para o teste

    Returns:
        dict: Resultado do teste (output, latência, tokens, custo)
    """
    logger.info(f"Iniciando teste: prompt_id={prompt_id}, version={version}")

    try:
        # TODO: Implementar lógica de execução em container Docker
        # 1. Criar container isolado
        # 2. Injetar prompt + variáveis
        # 3. Chamar provider LLM (Ollama, Groq, OpenAI, etc)
        # 4. Coletar métricas (latência, tokens, custo)
        # 5. Persistir resultado no banco

        result = {
            "prompt_id": prompt_id,
            "version": version,
            "output": "Teste em desenvolvimento",
            "latency_ms": 0,
            "tokens_used": 0,
            "cost_usd": 0.0,
            "status": "pending",
        }

        logger.info(f"Teste finalizado: {prompt_id}")
        return result

    except Exception as e:
        logger.error(f"Erro ao executar teste: {str(e)}", exc_info=True)
        raise


# Importar para que o Celery descubra as tasks
__all__ = ["execute_test"]
