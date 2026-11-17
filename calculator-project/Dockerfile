# Use Python slim image (smaller than standard Python image)
FROM python:3.11-alpine

# Set the working directory inside the container
WORKDIR /app

# Install only production dependencies (build tools already in Alpine image)
# (pytest and httpx are test-only and excluded from the production image)
COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn \
    && rm -rf /root/.cache

# Copy the application source code
COPY app/ ./app/

# Copy the static frontend files
COPY static/ ./static/

# Create a non-root user and change ownership
RUN adduser -D appuser && chown -R appuser:appuser /app
USER appuser

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Run the FastAPI application with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
