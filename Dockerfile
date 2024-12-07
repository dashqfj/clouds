# Используем Python-образ
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY . .

# Открываем порт Flask-приложения
EXPOSE 5000

# Запуск приложения
CMD ["python", "app.py", "flask", "run", "--host=0.0.0.0", "--port=5000"]
