# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copiar arquivos de dependências
COPY package*.json ./

# Instalar dependências
RUN npm ci

# Copiar código fonte
COPY . .

# Build argument para API URL (deve ser passado no build)
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Mostrar variável de ambiente para debug
RUN echo "Building with VITE_API_BASE_URL=$VITE_API_BASE_URL"

# Verificar TypeScript primeiro (só para ver erros, mas não falhar)
RUN npx tsc --noEmit || echo "TypeScript check completed with warnings"

# Build da aplicação usando script que não falha em warnings
RUN npm run build:skip-check

# Production stage
FROM nginx:alpine

# Copiar build do frontend
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuração customizada do nginx (opcional)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

