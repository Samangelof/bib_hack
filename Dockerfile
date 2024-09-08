# Используем базовый образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем pipenv
RUN pip install --upgrade pip && pip install pipenv

# Копируем файлы pipenv для установки зависимостей
COPY Pipfile Pipfile.lock /app/

# Устанавливаем зависимости через pipenv с флагом --system
RUN pipenv install --system --deploy

# Копируем оставшиеся файлы проекта в контейнер
COPY . /app/

# Выполняем миграции и собираем статику
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Открываем порт 8000 для доступа
EXPOSE 8000

# Команда для запуска приложения через Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "library_hack.wsgi:application"]
