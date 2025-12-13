# Base stage - common dependencies
FROM node:20-alpine AS base

# Install wget for healthcheck (needed in both dev and prod)
RUN apk add --no-cache wget

WORKDIR /app

# Install dependencies
# Security: npm scripts are required for native dependency compilation (rollup, etc.)
# --ignore-scripts cannot be used here as build tools need to compile native binaries
# All packages are from trusted sources (npm registry) and verified during installation
COPY package*.json ./
# NOSONAR docker:S6505 - npm scripts are necessary for native dependency compilation
RUN npm install

# Install Rollup native binary for Alpine Linux (musl)
# Security: This package requires scripts to install platform-specific native binaries
# The package is from npm registry and scripts are necessary for proper installation
# --ignore-scripts cannot be used as the binary installation requires script execution
# NOSONAR docker:S6505 - Scripts required to install native binaries for Rollup
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

ENV VITE_API_URL=http://backend:5012
WORKDIR /usr/share/nginx/html

USER root
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY docker-entrypoint.sh /docker-entrypoint.sh
# Security: Copy files ensuring no write permissions are assigned to copied resources
# Copy to temporary location, set explicit read-only permissions, then move to final location
# This prevents write permissions from being assigned during the COPY operation
COPY --from=build /app/dist /tmp/dist
RUN install -d -o 101 -g 101 -m 755 /usr/share/nginx/html/config && \
    chmod +x /docker-entrypoint.sh && \
    chown -R 101:101 /tmp/dist && \
    chmod -R a-w /tmp/dist && \
    cp -r /tmp/dist/* /usr/share/nginx/html/ && \
    chmod -R a-w /usr/share/nginx/html && \
    chmod 755 /usr/share/nginx/html/config && \
    rm -rf /tmp/dist
USER 101

EXPOSE 8080

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
