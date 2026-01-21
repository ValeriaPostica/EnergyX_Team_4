FROM node:current-alpine AS builder

WORKDIR /app

COPY package.json ./

RUN npm install

COPY . .

RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY default.conf.template /etc/nginx/templates/default.conf.template

# Default values for environment variables
ENV BACKEND_IP=pbl-back 
ENV IOT_IP=pbl-iot

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

