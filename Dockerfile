<<<<<<< HEAD
FROM python:3.13-alpine

# Установите зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируйте приложение
COPY . /app

# Установите рабочую директорию
WORKDIR /app

# Сделайте скрипты исполняемыми
RUN chmod +x apply_migrations.sh wait_for_db.sh

# Устанавливаем команду для запуска приложения
CMD ["./wait_for_db.sh", "db", "sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
=======
# Используем официальный образ Python
FROM python:3.9

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Открываем порт 8000
EXPOSE 8000

# Запускаем сервер Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
>>>>>>> 64b7e42423bd59a48425a3142e5c98fb55252296
