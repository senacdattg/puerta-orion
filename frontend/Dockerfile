FROM node:20 AS build

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm install --no-save @rollup/rollup-linux-x64-gnu \
 && npm run build

FROM nginx:stable-alpine

ENV VITE_API_URL=http://backend:5000

RUN apk add --no-cache bash

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY docker-entrypoint.sh /docker-entrypoint.sh

RUN chmod +x /docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]