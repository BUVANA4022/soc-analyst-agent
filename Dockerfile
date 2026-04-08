FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your project files
COPY . .

# Expose the ports for FastAPI (8000) and Streamlit (7860)
EXPOSE 8000
EXPOSE 7860

# The Magic Command: Starts the API in the background and your UI in the foreground
CMD uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run app.py --server.port 7860 --server.address 0.0.0.0
