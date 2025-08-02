FROM python:3.9-slim

# Set working directory
WORKDIR /app

COPY . .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["python", "app.py"]