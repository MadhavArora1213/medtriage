FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port for Hugging Face Space
EXPOSE 7860

# Define environment variables with defaults
ENV API_BASE_URL="https://api.openai.com/v1"
ENV MODEL_NAME="gpt-4.1-mini"
ENV HF_TOKEN=""

# Run the environment server to keep the space 'Running'
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
