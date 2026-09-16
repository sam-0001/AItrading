FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir build && pip install -e .

COPY . .

# In Phase 14, main.py orchestrates the scheduler and dashboard
CMD ["python", "main.py"]
