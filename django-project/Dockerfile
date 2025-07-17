FROM python:3.11-slim-bookworm

WORKDIR /app

RUN pip install uv
# Copy requirements and sync
COPY requirements.txt .
# Install dependencies using uv
RUN uv sync --locked

# Copy project files
COPY . .

EXPOSE 8000

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
