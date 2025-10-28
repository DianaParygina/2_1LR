# -- 1 Этап сборки фронтенда ---
FROM node:20-alpine AS frontend-build
WORKDIR /app

# Копируем package*.json из папки client в корень проекта
COPY client/package*.json ./

RUN npm install

# Копируем сам клиентский код
COPY client/ .
RUN npm run build

# --- 2 Этап запуска nginx ---
FROM nginx:alpine

# Копируем кастомный конфиг
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Копируем собранную статику из папки 'dist' (обычно в Vite)
COPY --from=frontend-build /app/dist /usr/share/nginx/html