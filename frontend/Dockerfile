# =============================
# Stage 1: Build React + Vite
# =============================
FROM node:20-alpine AS builder

# Рабочая директория
WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

# =============================
# Stage 2: Serve with Nginx
# =============================
FROM nginx:alpine

RUN rm -rf /usr/share/nginx/html/*

COPY --from=builder /app/dist /usr/share/nginx/html

# Expose порт
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
