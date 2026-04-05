"""
🚀 SandboxAI — Backend FastAPI

Aplicação principal para versionamento e teste de prompts para LLMs.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api import auth, metrics, prompts, providers, tests, versions
from app.core.database import dispose_engine, engine

# Criar aplicação FastAPI
app = FastAPI(
    title="SandboxAI API",
    description="Plataforma de versionamento, teste e comparação de prompts para LLMs",
    version="1.0.0",
    servers=[
        {"url": "http://localhost:8000", "description": "Local development"},
        {"url": "http://api:8000", "description": "Docker environment"},
    ],
)

# Middleware CORS
allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(
        ","
    )
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers
app.include_router(auth.router)
app.include_router(prompts.router)
app.include_router(versions.router)
app.include_router(tests.router)
app.include_router(metrics.router)
app.include_router(providers.router)


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Validate database connection on startup."""
    print("🚀 Validating database connection...")
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

            # Check if tables exist
            tables_stmt = text(
                """
                SELECT
                    to_regclass('public.users') IS NOT NULL AS has_users,
                    to_regclass('public.alembic_version') IS NOT NULL AS has_alembic
                """
            )
            result = await conn.execute(tables_stmt)
            status_row = result.mappings().one()

            if not status_row["has_users"] or not status_row["has_alembic"]:
                print("❌ Critical database schema is missing (users/alembic_version).")
                print("Please run migrations manually: alembic upgrade head")
                # We raise error here to stop startup without modifying anything
                raise RuntimeError("Database schema missing. Manual intervention required.")

            print("✅ Database connection validated")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    print("🔌 Disposing database connections...")
    await dispose_engine()
    print("✅ Database connections closed")


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Verificação de saúde da aplicação.

    Returns:
        dict: Status da aplicação
    """
    return {"status": "healthy", "service": "sandboxai-api", "version": "1.0.0"}


# Root endpoint
@app.get("/")
async def root():
    """
    Endpoint raiz da API.

    Returns:
        dict: Informações sobre a API
    """
    return {
        "message": "Bem-vindo ao SandboxAI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Handler global de exceções.

    Args:
        request: Requisição HTTP
        exc: Exceção capturada

    Returns:
        JSONResponse: Resposta com erro
    """
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor", "type": type(exc).__name__},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
