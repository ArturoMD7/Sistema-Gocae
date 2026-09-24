FROM node:20-alpine

WORKDIR /app

# Usar pnpm (instalándolo globalmente)
RUN npm install -g pnpm

COPY package.json pnpm-lock.yaml* ./

# Instalar dependencias
RUN pnpm install

COPY . .

# Exponer el puerto de Vite
EXPOSE 5173
