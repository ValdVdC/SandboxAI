# ═══════════════════════════════════════════════════════════════════════════
# ⚛️  Frontend Dockerfile — React + TypeScript + Vite (Multi-stage build)
# ═══════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 1: BUILDER — Compilar React + TypeScript
# ─────────────────────────────────────────────────────────────────────────────

FROM node:20-alpine AS builder

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependências
RUN npm install

# Copiar código fonte
COPY . .

# Build do projeto
RUN npm run build

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 2: DEVELOPMENT — Servidor de desenvolvimento (Vite)
# ─────────────────────────────────────────────────────────────────────────────

FROM node:20-alpine AS development

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependências em modo desenvolvimento
RUN npm install

# Copiar código fonte
COPY . .

# Criar usuário não-root (usar ID 10001 para evitar conflitos em Alpine)
RUN addgroup -g 10001 appuser && \
    adduser -D -u 10001 -G appuser appuser && \
    chown -R appuser:appuser /app

USER appuser

# Variáveis de ambiente
ENV NODE_ENV=development

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

# Exposição de porta
EXPOSE 3000

# Comando padrão para desenvolvimento
CMD ["npm", "run", "dev"]

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 3: PRODUCTION — Servir com Nginx
# ─────────────────────────────────────────────────────────────────────────────

FROM nginx:alpine AS production

# Configurar Nginx
COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx-default.conf /etc/nginx/conf.d/default.conf

# Copiar build do builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Criar usuário não-root para Nginx
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser && \
    chown -R appuser:appuser /usr/share/nginx/html

USER appuser

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

# Exposição de porta
EXPOSE 80

# Nginx roda em foreground por padrão

# ═══════════════════════════════════════════════════════════════════════════
# LABELS — Metadados da imagem
# ═══════════════════════════════════════════════════════════════════════════

LABEL maintainer="SandboxAI Team" \
      version="1.0.0" \
      description="Frontend React + TypeScript para SandboxAI — Plataforma de teste de prompts para LLMs"
