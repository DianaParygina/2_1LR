# Стейдж 1: Builder (Сборка статических файлов)
# Используем Node.js для сборки фронтенда (Vite, React, Vue и т.д.)
FROM node:20-alpine AS builder

WORKDIR /app

# Копируем файлы package.json для установки зависимостей
COPY client/package*.json ./

# Установка зависимостей
RUN npm install

# Копируем исходный код фронтенда
COPY client/ ./

# Запуск сборки (команда зависит от вашего package.json, обычно 'build')
RUN npm run build

# -------------------------------------------------------------

# Стейдж 2: Production (Обслуживание статики через Nginx)
# Используем минимальный образ Nginx
FROM nginx:alpine

# Копируем конфигурацию Nginx (если она вам нужна)
# Если у вас есть файл nginx.conf для продакшена в корне, скопируйте его сюда.
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Удаляем дефолтные статические файлы Nginx
RUN rm -rf /usr/share/nginx/html/*

# Копируем собранные статические файлы из 'builder' стейджа в папку Nginx
# В вашем случае, судя по структуре Vite, папка сборки называется `dist`.
COPY --from=builder /app/dist /usr/share/nginx/html

# Заменяем конфигурацию Nginx по умолчанию, чтобы убедиться, что он может
# обслуживать статические файлы и, при необходимости, проксировать API-запросы на бэкенд.
# Для простоты лабораторной, просто обслуживаем статику.
COPY client/nginx.conf /etc/nginx/conf.d/default.conf

# Порт Nginx
EXPOSE 80

# Nginx запускается по умолчанию
CMD ["nginx", "-g", "daemon off;"]