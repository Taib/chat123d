FROM python:3.12-slim

RUN adduser --system --group --no-create-home liboo
USER root

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

RUN chmod +x ./start.sh

USER liboo

# Run the application.
ENTRYPOINT ["/app/start.sh"]