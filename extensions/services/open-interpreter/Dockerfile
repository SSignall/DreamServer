FROM python:3.11-slim

# Install dependencies
RUN pip install --no-cache-dir open-interpreter fastapi uvicorn

# Expose port
EXPOSE 8000

# Create data directory
RUN mkdir -p /root/.open-interpreter

# Default command: start FastAPI server
CMD ["python", "-m", "interpreter", "server"]
