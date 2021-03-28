# Install dependencies
FROM arm32v7/python:3.9-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install pip-tools
RUN pip-sync requirements.txt --pip-args '--no-cache-dir --user'

# Copy application
COPY kupcimat kupcimat
COPY mapping-schema.yaml .
COPY webthings-server.py .

# Build production image
FROM arm32v7/python:3.9-alpine
COPY --from=build /root/.local/lib/python3.9/site-packages /app/site-packages
COPY --from=build /app /app
WORKDIR /app
ENV PYTHONPATH /app/site-packages
CMD ["python", "webthings-server.py"]
