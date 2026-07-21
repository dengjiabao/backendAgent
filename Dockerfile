FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
ENV PYTHONPATH=/app/src
EXPOSE 8000
CMD ["uvicorn", "ecommerce_agent.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
