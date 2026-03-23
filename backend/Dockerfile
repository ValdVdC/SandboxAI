# ═══════════════════════════════════════════════════════════════════════════
# 🐍 Backend Dockerfile — Python 3.11 + FastAPI (Multi-stage build)
# ═══════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 1: BUILDER — Instalar dependências Python
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependências de sistema necessárias para compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivo de dependências
COPY requirements.txt .

# Criar virtualenv e instalar dependências
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 2: RUNTIME — Imagem final otimizada
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim AS runtime

WORKDIR /app

# Instalar apenas dependências de runtime (sem build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar virtualenv do builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar código da aplicação
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY run_migrations.py ./
COPY entrypoint.sh ./
COPY .dockerignore ./

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 sandboxai && \
    chown -R sandboxai:sandboxai /app

USER sandboxai

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando padrão
CMD ["./entrypoint.sh"]

# ═══════════════════════════════════════════════════════════════════════════
# LABELS — Metadados da imagem
# ═══════════════════════════════════════════════════════════════════════════

LABEL maintainer="SandboxAI Team" \
      version="1.0.0" \
      description="Backend API FastAPI para SandboxAI — Plataforma de teste de prompts para LLMs"
