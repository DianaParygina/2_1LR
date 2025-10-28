# 1. Используем официальный базовый образ Python
FROM python:3.12-slim

# 2. Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# 3. Копируем файл зависимостей и устанавливаем их
# Это нужно делать первым, чтобы кэшировать слой (если requirements.txt не меняется)
COPY requirements.txt /app/

# Устанавливаем системные зависимости, необходимые для некоторых Python-пакетов
# (например, для компиляции пакетов, использующих С-расширения)
RUN apt-get update && apt-get install -y build-essential \ 
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем весь остальной код приложения
COPY . /app/

# 5. Собираем статические файлы (STATIC_ROOT должен быть настроен в settings.py)
RUN python manage.py collectstatic --noinput

# 6. Определяем порт, который будет слушать Gunicorn
EXPOSE 8000

# 7. Задаем команду, которая будет выполнена при запуске контейнера
# (1) Выполняем миграции БД.
# (2) Запускаем Gunicorn, который будет слушать порт 8000.
# Замените `app.wsgi:application` на правильный путь, если ваш wsgi.py находится в другом месте.
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn app.wsgi:application --bind 0.0.0.0:8000"]