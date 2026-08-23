FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y \
        curl \
        ca-certificates \
        gnupg \
        unixodbc \
        unixodbc-dev \
    && curl -sSL \
        https://packages.microsoft.com/keys/microsoft.asc \
        | gpg --dearmor \
        -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -sSL \
        https://packages.microsoft.com/config/debian/12/prod.list \
        -o /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "gunicorn main:app --worker-class uvicorn_worker.UvicornWorker --workers ${WEB_CONCURRENCY:-2} --bind 0.0.0.0:${PORT:-8000} --timeout 180 --access-logfile - --error-logfile -"]