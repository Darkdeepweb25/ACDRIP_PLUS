FROM python:3.11-slim

# Install nmap
RUN apt-get update && \
    apt-get install -y --no-install-recommends nmap && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ /app/
COPY frontend/ /app/frontend/

# Create reports directory
RUN mkdir -p /app/reports_output

# Expose port
EXPOSE 8000

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DEBUG=false
ENV DATABASE_URL=sqlite:///./acdrip_plus.db

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
