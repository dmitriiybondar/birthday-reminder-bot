FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Kyiv

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    tzdata \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN useradd -m botuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R botuser:botuser /app
USER botuser

CMD ["python", "bot.py"]