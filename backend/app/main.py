"""
🚀 SandboxAI — Backend FastAPI

Aplicação principal para versionamento e teste de prompts para LLMs.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
from app.core.database import init_db, dispose_engine
from app.api import auth, prompts, versions, tests, metrics

# Criar aplicação FastAPI
app = FastAPI(
    title="SandboxAI API",
    description="Plataforma de versionamento, teste e comparação de prompts para LLMs",
    version="1.0.0",
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Local development"
        },
        {
            "url": "http://api:8000",
            "description": "Docker environment"
        }
    ]
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, configurar com variáveis de ambiente
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


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    print("🚀 Initializing database...")
    await init_db()
    print("✅ Database initialized successfully")


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
    return {
        "status": "healthy",
        "service": "sandboxai-api",
        "version": "1.0.0"
    }


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
        "health": "/health"
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
        content={
            "detail": "Erro interno do servidor",
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
