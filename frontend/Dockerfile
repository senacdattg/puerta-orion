FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY vite.config.js ./
COPY jsconfig.json ./
COPY eslint.config.js ./
COPY index.html ./
COPY public ./public
COPY src ./src

ARG ROLLUP_BINARY_PACKAGE=@rollup/rollup-linux-x64-musl
RUN npm install --no-save "${ROLLUP_BINARY_PACKAGE}" \
    && npm run build

FROM nginxinc/nginx-unprivileged:1.25-alpine AS runtime

ENV VITE_API_URL=http://backend:5000
WORKDIR /usr/share/nginx/html

USER root
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY --chown=101:101 --from=build /app/dist ./
RUN install -d -o 101 -g 101 config && chmod +x /docker-entrypoint.sh
USER 101

EXPOSE 8080

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]