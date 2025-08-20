# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . .

# Устанавливаем зависимости
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Указываем команду запуска приложения
CMD ["python", "app.py"]
