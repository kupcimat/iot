# Install dependencies
FROM arm32v7/python:3.8-slim AS build
WORKDIR /app
COPY Pipfile .
COPY Pipfile.lock .
RUN pip install pipenv
RUN pipenv install

# Copy application
COPY kupcimat kupcimat
COPY webthings-server.py .

# Build production image
FROM arm32v7/python:3.8-alpine
COPY --from=build /root/.local/share/virtualenvs/app-4PlAip0Q/lib/python3.8/site-packages /app/site-packages
COPY --from=build /app /app
WORKDIR /app
ENV PYTHONPATH /app/site-packages
CMD ["python", "webthings-server.py"]
