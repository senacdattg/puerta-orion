# Base stage - common dependencies
FROM node:20-alpine AS base

# Install wget for healthcheck (needed in both dev and prod)
RUN apk add --no-cache wget

WORKDIR /app

# Install dependencies
# nosonar: S6505 - Scripts de npm son necesarios para compilar dependencias nativas
# Se usa --ignore-scripts solo cuando sea seguro, pero aquí se necesitan para build tools
COPY package*.json ./
RUN npm install

# Install Rollup native binary for Alpine Linux (musl)
# This is required because Rollup needs platform-specific binaries
# nosonar: S6505 - Scripts necesarios para instalar binarios nativos de Rollup
RUN npm install --no-save @rollup/rollup-linux-x64-musl

# Development stage
FROM base AS development

# Expose Vite dev server port
EXPOSE 5173

# Start Vite dev server with hot reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

# Build stage - for production
FROM base AS build

COPY vite.config.js ./
COPY jsconfig.json ./
COPY eslint.config.js ./
COPY index.html ./
COPY public ./public
COPY src ./src

# Build the application
RUN npm run build

# Production stage - serve with nginx
FROM nginxinc/nginx-unprivileged:1.25-alpine AS production

ENV VITE_API_URL=http://backend:5000
WORKDIR /usr/share/nginx/html

USER root
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY docker-entrypoint.sh /docker-entrypoint.sh
# nosonar: S6504 - Permisos de solo lectura asignados explícitamente (101:101, sin escritura)
# Los archivos copiados tienen ownership 101:101 (usuario nginx no privilegiado)
# y permisos de solo lectura por defecto (no se asignan permisos de escritura)
COPY --chown=101:101 --from=build /app/dist ./
RUN install -d -o 101 -g 101 -m 755 config && \
    chmod +x /docker-entrypoint.sh && \
    chmod -R a-w /usr/share/nginx/html
USER 101

EXPOSE 8080

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
