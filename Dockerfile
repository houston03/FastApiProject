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
CMD ["uvicorn", "./wait_for_db.sh", "db", "sh", "-c", "alembic upgrade head && fastApiProject.src.app.main:app --host 0.0.0.0 --port 8000"]